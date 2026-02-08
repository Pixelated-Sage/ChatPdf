from google import genai
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

async def test():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("No API key found")
        return

    try:
        client = genai.Client(api_key=api_key)
        print("Client initialized")
        
        response = await client.aio.models.generate_content(
            model='gemini-flash-lite-latest',
            contents='Hello'
        )
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
