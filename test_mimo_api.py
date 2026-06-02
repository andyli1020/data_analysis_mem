#!/usr/bin/env python
"""
Test script for MiMo AI API integration.

This script tests the connection to MiMo-v2.5-pro API and verifies
that the API key is working correctly.
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv


def load_environment():
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        print("Error: .env file not found")
        print("Please create a .env file with your MiMo API key:")
        print("MIMO_API_KEY=your_api_key_here")
        print("MIMO_BASE_URL=https://api.mimo.ai/v1")
        return False
    
    load_dotenv(env_path)
    
    api_key = os.getenv("MIMO_API_KEY")
    base_url = os.getenv("MIMO_BASE_URL", "https://api.mimo.ai/v1")
    
    if not api_key:
        print("Error: MIMO_API_KEY not set in .env file")
        return False
    
    print(f"✓ API Key loaded: {api_key[:10]}...{api_key[-4:]}")
    print(f"✓ Base URL: {base_url}")
    
    return True


def test_api_connection():
    """Test the MiMo API connection."""
    api_key = os.getenv("MIMO_API_KEY")
    base_url = os.getenv("MIMO_BASE_URL", "https://api.mimo.ai/v1")
    
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }
    
    # Simple test message
    data = {
        "model": "mimo-v2.5-pro",
        "messages": [
            {
                "role": "system",
                "content": "You are MiMo, an AI assistant developed by Xiaomi. Today is date: Tuesday, December 16, 2025. Your knowledge cutoff date is December 2024."
            },
            {
                "role": "user",
                "content": "Hello, please introduce yourself briefly."
            }
        ],
        "max_completion_tokens": 100
    }
    
    url = f"{base_url}/chat/completions"
    
    print(f"\nTesting API connection to: {url}")
    print("Sending test request...")
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✓ API connection successful!")
            print(f"Response ID: {result.get('id', 'N/A')}")
            print(f"Model: {result.get('model', 'N/A')}")
            
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0].get("message", {}).get("content", "")
                print(f"\nAI Response:\n{content[:200]}...")
            
            if "usage" in result:
                usage = result["usage"]
                print(f"\nToken Usage:")
                print(f"  Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
                print(f"  Completion tokens: {usage.get('completion_tokens', 'N/A')}")
                print(f"  Total tokens: {usage.get('total_tokens', 'N/A')}")
            
            return True
        else:
            print(f"✗ API request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ Request timed out (30 seconds)")
        return False
    except requests.exceptions.ConnectionError:
        print("✗ Connection error. Please check your internet connection.")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def test_translation():
    """Test translation functionality."""
    api_key = os.getenv("MIMO_API_KEY")
    base_url = os.getenv("MIMO_BASE_URL", "https://api.mimo.ai/v1")
    
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }
    
    test_text = "Artificial intelligence is transforming the way we work and live."
    
    data = {
        "model": "mimo-v2.5-pro",
        "messages": [
            {
                "role": "system",
                "content": "你是一个专业的翻译助手。请将以下英文文本翻译成中文，保持原文的格式和风格，确保翻译准确自然。"
            },
            {
                "role": "user",
                "content": test_text
            }
        ],
        "max_completion_tokens": 200
    }
    
    url = f"{base_url}/chat/completions"
    
    print(f"\nTesting translation functionality...")
    print(f"Original text: {test_text}")
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                translated = result["choices"][0].get("message", {}).get("content", "")
                print(f"Translated text: {translated}")
                return True
        
        print(f"✗ Translation test failed: {response.status_code}")
        return False
        
    except Exception as e:
        print(f"✗ Translation test error: {e}")
        return False


def main():
    """Main test function."""
    print("=" * 50)
    print("MiMo AI API Test Suite")
    print("=" * 50)
    
    # Load environment
    if not load_environment():
        sys.exit(1)
    
    # Test API connection
    print("\n" + "=" * 50)
    print("Test 1: API Connection")
    print("=" * 50)
    
    if not test_api_connection():
        print("\n⚠ API connection test failed. Please check:")
        print("1. Your API key is correct")
        print("2. You have internet connection")
        print("3. The API endpoint is accessible")
        sys.exit(1)
    
    # Test translation
    print("\n" + "=" * 50)
    print("Test 2: Translation Functionality")
    print("=" * 50)
    
    if not test_translation():
        print("\n⚠ Translation test failed")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✓ All tests passed!")
    print("=" * 50)
    print("\nYour MiMo AI integration is ready to use.")
    print("You can now use the mimo-ai skill in your projects.")


if __name__ == "__main__":
    main()