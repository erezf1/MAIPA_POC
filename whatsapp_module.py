import subprocess
import os
import json
import time

# Constants
CONNECTED_FILE = 'static/connected.json'
GROUPS_FILE = 'static/groups.json'
MESSAGE_FILE_TEMPLATE = 'static/messages_{group_id}.json'

# Generate a QR code for WhatsApp connection
def generate_qr():
    """Generates a QR code by running the Node.js script."""
    try:
        # Run the JS script and capture output
        result = subprocess.run(
            ["node", "generate_qr.js"],
            text=True,  # Ensure output is captured as a string
            capture_output=True  # Capture stdout and stderr
        )

        # Print the output from the JS script
        print("QR Code JS Output (stdout):", result.stdout)
        if result.stderr:
            print("QR Code JS Error (stderr):", result.stderr)

    except Exception as e:
        print(f"Error running generate_qr.js: {e}")
# Check if the WhatsApp connection is active
def check_connection():
    """Checks if the WhatsApp connection is active by reading from the connection file."""
    if os.path.exists(CONNECTED_FILE):
        with open(CONNECTED_FILE, 'r') as f:
            connected_data = json.load(f)
        return connected_data.get('connected', False)
    return False

# List available WhatsApp groups from the JSON file
def list_groups():
    """Returns a list of available WhatsApp groups."""
    if os.path.exists(GROUPS_FILE):
        with open(GROUPS_FILE, 'r', encoding='utf-8') as f:
            groups = json.load(f)
        return groups
    else:
        print("No groups found. Please ensure you are connected.")
        return []

# Fetch latest messages, simulating a WhatsApp fetch with realistic constraints
def fetch_latest_messages(group_id, limit=100, before=None):
    """Simulates the fetching of the latest WhatsApp messages."""
    current_time = time.time() if before is None else before
    available_message_count = 200  # Simulate available messages

    # Calculate number of messages to fetch
    fetch_count = min(available_message_count, limit)
    messages = [
        {"id": f"{group_id}_{i}", "message": f"Message {i}", 
         "timestamp": current_time - i * 60}
        for i in range(fetch_count)
    ]

    available_message_count -= fetch_count  # Simulate depletion of messages
    return messages if available_message_count > 0 else []

# Download messages using an external JavaScript script
def download_messages(group_id):
    """Downloads messages from the selected group using the JS script."""
    print(f"Downloading messages for group {group_id}...")
    subprocess.run(["node", "download_messages.js", group_id])
    print("Message download completed.")

# Verify if messages from the last 24 hours exist in the downloaded file
def verify_recent_messages(group_id):
    """Verifies if messages from the last 24 hours are available."""
    file_path = MESSAGE_FILE_TEMPLATE.format(group_id=group_id)
    if not os.path.exists(file_path):
        print(f"No message file found for group {group_id}.")
        return False

    with open(file_path, 'r', encoding='utf-8') as f:
        messages = json.load(f)

    now = time.time()
    twenty_four_hours_ago = now - (24 * 60 * 60)
    recent_messages = [msg for msg in messages if msg['timestamp'] >= twenty_four_hours_ago]

    print(f"Found {len(recent_messages)} messages from the last 24 hours.")
    return len(recent_messages) > 0

# Fetch group messages in batches of 24 hours (extendable logic)
def fetch_group_messages(group_id, last_timestamp=None):
    """Fetches all messages for a group, divided into 24-hour batches."""
    all_messages = []
    current_time = time.time() if last_timestamp is None else last_timestamp

    while True:
        messages = fetch_latest_messages(group_id, limit=100, before=current_time)
        if not messages:
            break
        all_messages.extend(messages)
        current_time = messages[-1]['timestamp'] - 1  # Move to the next batch

    print(f"Fetched {len(all_messages)} messages for group {group_id}.")
    return all_messages

# Save fetched messages to a file
def save_messages(group_id, messages):
    """Saves messages to a JSON file."""
    file_path = MESSAGE_FILE_TEMPLATE.format(group_id=group_id)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(messages, f, indent=2)
    print(f"Messages saved to {file_path}.")

# Example usage flow (for testing purposes)
if __name__ == "__main__":
    generate_qr()  # Generate QR code for login
    connected = check_connection()
    if not connected:
        print("Not connected. Please scan the QR code.")
    else:
        groups = list_groups()
        if groups:
            print("Available groups:")
            for group in groups:
                print(f"ID: {group['id']} | Name: {group['name']}")
            
            group_id = input("Enter the group ID to download messages: ")
            download_messages(group_id)

            if verify_recent_messages(group_id):
                print("Recent messages found. Proceeding with analysis...")
            else:
                print("No recent messages found.")
