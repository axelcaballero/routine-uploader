#!/usr/bin/env python3
"""
Utility script for managing Hevy routine folders.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hevy_api_client import HevyAPIClient


def list_folders():
    """List all routine folders."""
    try:
        client = HevyAPIClient()
        response = client.list_routine_folders(page=1, page_size=10)
        
        folders = response.get('routine_folders', [])
        
        if not folders:
            print("No folders found.")
            return
        
        print("\n=== Your Routine Folders ===\n")
        print(f"{'Folder Name':<30} {'Folder ID':<15} {'Index'}")
        print("-" * 60)
        
        for folder in folders:
            name = folder.get('title', 'Unknown')
            folder_id = folder.get('id', 'Unknown')
            index = folder.get('index', 'N/A')
            print(f"{name:<30} {str(folder_id):<15} {index}")
        
        print(f"\nTotal folders: {len(folders)}")
        
    except Exception as e:
        print(f"Error listing folders: {e}")
        sys.exit(1)


def create_folder(folder_name):
    """Create a new routine folder."""
    try:
        client = HevyAPIClient()
        
        print(f"Creating folder: {folder_name}...")
        response = client.create_routine_folder(folder_name)
        
        if 'routine_folder' in response:
            folder = response['routine_folder']
            folder_id = folder.get('id')
            print(f"\n✅ Folder created successfully!")
            print(f"   Folder ID: {folder_id}")
            print(f"   Name: {folder.get('title')}")
            print(f"   Index: {folder.get('index')}")
            
            # Return the folder ID for use in other operations
            return folder_id
        else:
            print(f"Error: Unexpected response format")
            print(json.dumps(response, indent=2))
            sys.exit(1)
            
    except Exception as e:
        print(f"Error creating folder: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Manage Hevy routine folders"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List command
    subparsers.add_parser("list", help="List all routine folders")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new routine folder")
    create_parser.add_argument("name", help="Name for the new folder")
    
    args = parser.parse_args()
    
    if args.command == "list":
        list_folders()
    elif args.command == "create":
        create_folder(args.name)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
