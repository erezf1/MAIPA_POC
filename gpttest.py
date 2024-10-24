import openai
import os

# Retrieve the API key securely from environment variables
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

# Function to query OpenAI GPT-4
def ask_gpt4(question):
    """Send a question to GPT-4 and return the response."""
    try:
        response = openai.ChatCompletion.create(
            api_key=api_key,
            model="gpt-4",  # Use the correct model name
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question}
            ],
            max_tokens=100,
            temperature=0.7
        )
        return response.choices[0].message.content

    except openai.error.AuthenticationError as e:
        print(f"Authentication error: {e}")
    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
    return None

def main():
    """Main function to test GPT-4 with a sample question."""
    question = "How many countries are in the European Union?"
    answer = ask_gpt4(question)

    if answer:
        print("Question:", question)
        print("Answer:", answer)
    else:
        print("Failed to retrieve an answer.")

if __name__ == "__main__":
    main()
