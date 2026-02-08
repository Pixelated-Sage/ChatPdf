from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

def test():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("No API key found")
        return

    client = genai.Client(api_key=api_key)
    
    # List models
    print("Listing available models:")
    try:
        pager = client.models.list()
        for model in pager:
            if 'gemini' in model.name:
                print(f"- {model.name}")
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    test()
