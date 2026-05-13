#!/usr/bin/env python3
"""
Get the most recent routine folder created.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hevy_api_client import HevyAPIClient

def main():
    try:
        client = HevyAPIClient()
        print("🔍 Fetching routine folders from Hevy API...")
        
        response = client.list_routine_folders(page=1, page_size=10)
        folders = response.get('routine_folders', [])
        
        if not folders:
            print("❌ No folders found")
            return None
        
        print(f"\n✅ Found {len(folders)} folder(s):\n")
        print(f"{'Rank':<5} {'Folder Name':<40} {'Index':<10} {'ID':<20}")
        print("-" * 75)
        
        for idx, folder in enumerate(folders, 1):
            name = folder.get('title', 'Unknown')
            folder_id = folder.get('id', 'Unknown')
            index = folder.get('index', 'N/A')
            print(f"{idx:<5} {name:<40} {str(index):<10} {str(folder_id):<20}")
        
        # Most recent is typically first in the list
        most_recent = folders[0]
        most_recent_name = most_recent.get('title', 'Unknown')
        
        print(f"\n📌 Most Recent Folder: {most_recent_name}")
        return most_recent_name
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    folder_name = main()
    if folder_name:
        sys.exit(0)
    else:
        sys.exit(1)
