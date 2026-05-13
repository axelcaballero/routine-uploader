#!/usr/bin/env python3
"""
Create a new routine folder with auto-incremented naming.
Intelligently determines the next folder name (e.g., HSF 15 → HSF 16).
"""

import sys
import os
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hevy_api_client import HevyAPIClient

def extract_number(folder_name: str) -> int:
    """Extract the numeric suffix from a folder name (e.g., 'HSF 15' -> 15)."""
    match = re.search(r'(\d+)$', folder_name)
    return int(match.group(1)) if match else 0

def get_prefix(folder_name: str) -> str:
    """Extract the prefix from a folder name (e.g., 'HSF 15' -> 'HSF ')."""
    match = re.match(r'^([A-Za-z\s]+)', folder_name)
    return match.group(1) if match else "HSF "

def find_next_folder_name(client: HevyAPIClient) -> str:
    """Determine the next folder name based on existing folders."""
    try:
        response = client.list_routine_folders(page=1, page_size=10)
        folders = response.get('routine_folders', [])
        
        if not folders:
            return "HSF 1"
        
        # Get the most recent folder
        most_recent = folders[0].get('title', 'HSF 1')
        prefix = get_prefix(most_recent)
        current_number = extract_number(most_recent)
        next_number = current_number + 1
        
        return f"{prefix}{next_number}".strip()
    except Exception as e:
        print(f"Error determining next folder name: {e}")
        return None

def create_new_folder(folder_name: str) -> bool:
    """Create a new routine folder."""
    try:
        client = HevyAPIClient()
        
        print(f"\n🔄 Creating folder: {folder_name}...")
        response = client.create_routine_folder(folder_name)
        
        if 'routine_folder' in response:
            folder = response['routine_folder']
            folder_id = folder.get('id')
            index = folder.get('index')
            print(f"\n✅ Folder created successfully!")
            print(f"   Folder Name: {folder_name}")
            print(f"   Folder ID:   {folder_id}")
            print(f"   Index:       {index}")
            return True
        else:
            print(f"❌ Unexpected response format")
            import json
            print(json.dumps(response, indent=2))
            return False
            
    except Exception as e:
        print(f"❌ Error creating folder: {e}", file=sys.stderr)
        return False

def main():
    try:
        client = HevyAPIClient()
        
        # Determine next folder name
        next_folder = find_next_folder_name(client)
        if not next_folder:
            print("❌ Could not determine next folder name")
            return False
        
        print(f"\n📋 Current Setup:")
        print(f"   Next folder name: {next_folder}")
        
        # Ask for confirmation
        print(f"\n❓ Create new folder '{next_folder}'? (y/n): ", end='')
        response = input().strip().lower()
        
        if response != 'y':
            print("❌ Cancelled")
            return False
        
        # Create the folder
        success = create_new_folder(next_folder)
        
        if success:
            print(f"\n📌 Use this folder with:")
            print(f"   python routine_uploader.py file.json --folder-title \"{next_folder}\"")
            print(f"   python batch_routine_uploader.py file.json --folder-title \"{next_folder}\"")
        
        return success
        
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled")
        return False
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
