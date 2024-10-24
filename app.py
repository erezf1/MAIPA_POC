from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
import os
import json
import time
import shutil  # Import shutil to manage session folder

from whatsapp_module import (
    generate_qr, check_connection, list_groups, 
    fetch_latest_messages, download_messages, verify_recent_messages
)
from gpt_module import load_summary_prompts, generate_summary

app = Flask(__name__)
app.secret_key = 'supersecretkey'

def clear_session():
    """Clear the session folder to ensure fresh QR code generation."""
    session_folder = 'session'
    if os.path.exists(session_folder):
        shutil.rmtree(session_folder)  # Remove the session folder and its contents
        print('Session folder cleared.')

# Disable caching in development
@app.after_request
def add_header(response):
    """Disable caching to always load the latest templates."""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

CONNECTED_FILE = 'static/connected.json'

def is_connected():
    """Check if the user is already connected to WhatsApp."""
    if os.path.exists(CONNECTED_FILE):
        with open(CONNECTED_FILE, 'r') as f:
            data = json.load(f)
        return data.get('connected', False)
    return False

# ====== Signup and QR Code Handling ======

@app.route('/', methods=['GET', 'POST'])
def signup():
    """Signup route to collect the user's phone number."""
    if request.method == 'POST':
        phone_number = request.form['phone_number']
        session['phone_number'] = phone_number  # Store the phone number in session

        # Check if already connected
        if is_connected():
            return redirect(url_for('group_selection'))

        # Generate QR if not connected
        generate_qr()
        return redirect(url_for('generate_qr_route', phone_number=phone_number))

    return render_template('signup.html')  # Uses signup.html

@app.route('/generate_qr/<phone_number>')
def generate_qr_route(phone_number):
    """Route to display the QR code for WhatsApp login."""
    qr_code_path = 'static/qr_code.txt'

    if not os.path.exists(qr_code_path):
        flash('QR code generation failed.')
        return redirect(url_for('signup'))

    with open(qr_code_path, 'r') as f:
        qr_code_data = f.read()

    return render_template('qr_code.html', qr_code_data=qr_code_data, phone_number=phone_number)

# ====== Group Selection and Syncing ======

@app.route('/group_selection', methods=['GET', 'POST'])
def group_selection():
    """Route to display available WhatsApp groups."""
    groups = [{"id": "123", "name": "Test Group 1"}, {"id": "456", "name": "Test Group 2"}]  # Placeholder

    if request.method == 'POST':
        group_id = request.form['group_id']
        return redirect(url_for('analysis_criteria', group_id=group_id))

    return render_template('group_selection.html', groups=groups)

  
@app.route('/sync_messages/<group_id>', methods=['GET'])
def sync_messages(group_id):
    """Fetches new messages for a group."""
    file_path = f'static/messages_{group_id}.json'
    
    new_message_count = fetch_messages_from_last_24_hours(group_id, file_path)

    flash(f"Fetched {new_message_count} new messages.")
    return redirect(url_for('group_selection'))

def fetch_messages_from_last_24_hours(group_id, file_path):
    """Fetches new messages from the last 24 hours."""
    current_time = time.time()
    twenty_four_hours_ago = current_time - (24 * 60 * 60)

    new_messages = []
    oldest_timestamp = current_time

    while oldest_timestamp > twenty_four_hours_ago:
        batch_messages = fetch_latest_messages(group_id, 100, before=oldest_timestamp)

        if not batch_messages:
            break

        new_messages.extend(batch_messages)
        oldest_timestamp = min(msg['timestamp'] for msg in batch_messages)

    with open(file_path, 'r+', encoding='utf-8') as f:
        existing_messages = json.load(f)
        existing_messages.extend(new_messages)
        f.seek(0)
        json.dump(existing_messages, f)

    return len(new_messages)

# ====== Analysis Criteria and Summary Generation ======

@app.route('/analysis_criteria/<group_id>', methods=['GET', 'POST'])
def analysis_criteria(group_id):
    """Route to collect analysis criteria."""
    if request.method == 'POST':
        analysis_type = request.form['analysis_type']
        criteria = request.form['criteria']
        return redirect(url_for('show_results', group_id=group_id, analysis_type=analysis_type, criteria=criteria))

    return render_template('analysis_criteria.html')
  
@app.route('/show_results/<group_id>/<analysis_type>/<criteria>')
def show_results(group_id, analysis_type, criteria):
    """Route to display the analysis result."""
    # Placeholder: Simulate analysis result
    summary = {
        'summary': f'Summary of group {group_id} with analysis type {analysis_type}.',
        'messages_used': 10
    }
    return render_template('result.html', summary=summary)

# ====== Status and Utility Routes ======

@app.route('/check_status')
def check_status():
    """Checks if the WhatsApp connection is active."""
    connected = check_connection()
    return jsonify({'connected': connected})

@app.route('/account_creation', methods=['GET'])
def account_creation():
    """Account creation or login page."""
    return "Account creation or login page."

@app.route('/groups')
def list_groups_route():
    """Lists all available WhatsApp groups."""
    groups = list_groups()
    if groups:
        return render_template('group_selection.html', groups=groups)
    flash("No groups available. Please connect to WhatsApp first.")
    return redirect(url_for('generate_qr_route'))

@app.route('/select_summary/<group_id>', methods=['GET'])
def select_summary(group_id):
    """Allows the user to select a summary type."""
    return render_template('select_summary.html', group_id=group_id)

def parse_summary_to_structured_data(summary_text):
    """Parses summary text into structured data."""
    discussions = []
    for part in summary_text.split('discussion'):
        if part.strip():
            lines = part.strip().split('\n')
            discussions.append({
                'title': lines[0].replace('title:', '').strip(),
                'content': lines[1].strip(),
                'engagement': lines[2].replace('engagement:', '').strip(),
                'started_by': lines[3].replace('discussion started by', '').strip(),
                'time': lines[4].strip(),
            })
    return discussions

# ====== Run the Flask App ======
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)  # Disable Flask reloader

