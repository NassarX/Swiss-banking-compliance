import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_api_connection():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not found in environment variables")
        return False

    print(f"API key found: {api_key[:6]}...{api_key[-4:]}")

    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    data = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 100,
        "messages": [{"role": "user", "content": "What is 2+2?"}]
    }

    try:
        print("Testing API connection...")
        response = requests.post(url, headers=headers, json=data)
        print(f"Status code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("\nResponse from Claude:")
            print(result.get("content", [{}])[0].get("text", "No response"))
            print("\nAPI TEST SUCCESSFUL!")
            return True
        else:
            print(f"Error response: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False


if __name__ == "__main__":
    test_api_connection()