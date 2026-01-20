
import os
import sys
from dotenv import load_dotenv
import google.genai as genai

# Load env directly
load_dotenv(override=True)
api_key = os.getenv("GEMINI_API_KEY")

print(f"Testing Key: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")

if not api_key:
    print("No API Key found")
    sys.exit(1)

try:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model='gemini-flash-latest',
        contents='Say Hello'
    )
    print("Success! Response:", response.text)
except Exception as e:
    print("Error:", e)
