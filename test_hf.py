
import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

# Step 1: Find the project folder
BASE_DIR = Path(__file__).resolve().parent

# Step 2: Load the .env file
load_dotenv(BASE_DIR / ".env", override=True)

# Step 3: Get the Groq API key
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY is missing. Check your .env file."
    )

# Step 4: Connect to Groq
client = Groq(api_key=api_key)

print("Testing Groq API connection...")

try:
    # Step 5: Send a test question
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": "Say hello in one sentence."
            }
        ],
        max_tokens=100,
    )

    # Step 6: Display the answer
    message = response.choices[0].message

    print("\nSUCCESS! The API responded.")
    print("Finish reason:", response.choices[0].finish_reason)
    print("Content:", repr(message.content))
    print("Reasoning:", repr(getattr(message, "reasoning", None)))
except Exception as error:
    print("\nAPI TEST FAILED")
    print("Error type:", type(error).__name__)
    print("Error details:", error)
