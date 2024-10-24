import openai
import os
import json
import time
from dotenv import load_dotenv  # Correct import

# Load environment variables from .env
load_dotenv()

# Retrieve the API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY in the .env file.")

# Load summary prompts from a JSON file
def load_summary_prompts():
    """Loads the summary prompts from a JSON file."""
    try:
        with open('static/summary_prompts.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Summary prompts file not found.")
        return {}

# Generate summary using OpenAI's GPT-4 model
def generate_summary(prompt, messages):
    """Generates a summary using OpenAI GPT based on user-defined criteria."""
    try:
        response = openai.ChatCompletion.create(
            api_key=api_key,
            model="gpt-4",  # Ensure correct model version is specified
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{prompt}\n\nMessages:\n{format_messages(messages)}"}
            ],
            max_tokens=2000,
            temperature=0.7
        )

        # Extract the summary from the response
        summary = response.choices[0].message.content
        log_api_call(prompt, messages, summary, response['usage'])
        return summary

    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return None

# Format messages for use in the summary
def format_messages(messages):
    """Formats messages as a string for the summary prompt."""
    return "\n".join([f"{msg['body']}" for msg in messages])

# Log API calls to a JSON file
def log_api_call(prompt, messages, summary, usage):
    """Logs API calls, including the prompt, message count, and token usage."""
    log_data = {
        "timestamp": time.time(),
        "prompt": prompt,
        "message_count": len(messages),
        "summary": summary,
        "tokens_used": usage.get('total_tokens', 0),
        "tokens_input": usage.get('prompt_tokens', 0),
        "tokens_output": usage.get('completion_tokens', 0)
    }

    with open('static/api_logs.json', 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_data, indent=2) + ",\n")

# Example usage (for testing purposes)
def main():
    # Example messages for testing
    messages = [
        {"body": "Hello, how are you?"},
        {"body": "I am fine, thank you!"}
    ]
    prompt = "Summarize the conversation"

    summary = generate_summary(prompt, messages)
    if summary:
        print("Summary:", summary)
    else:
        print("Failed to generate summary.")

if __name__ == "__main__":
    main()
