#!/usr/bin/env python3
"""
Quick test script to verify your Hevy API credentials
"""

import json
import os
import sys

import requests

def test_api_key(api_key):
    """Test if the API key works"""
    url = "https://api.hevyapp.com/v1/routines"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def main() -> None:
    """Main entry point for auth verification."""
    if len(sys.argv) >= 2:
        api_key = sys.argv[1]
    else:
        api_key = os.getenv("HEVY_API_KEY")

    if not api_key:
        print("Usage: python scripts/test_api_key.py <api_key>")
        print("\nOr set HEVY_API_KEY environment variable")
        raise SystemExit(1)

    print(f"Testing API key: {api_key[:8]}...")

    if test_api_key(api_key):
        print("\n✅ API key is valid!")
        return

    print("\n❌ API key is invalid or expired")
    print("\nTroubleshooting steps:")
    print("1. Verify your account is Hevy Pro/Premium")
    print("2. Generate a new API key at: https://hevy.com/settings?developer")
    print("3. Make sure you copied the key exactly with no spaces")
    raise SystemExit(1)

if __name__ == "__main__":
    main()
