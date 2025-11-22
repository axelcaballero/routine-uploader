#!/usr/bin/env python3
"""
Script to upload routine JSON files to Hevy API.
"""

import json
import sys
from pathlib import Path
from hevy_api_client import HevyAPIClient


def upload_routine_from_file(file_path: str, dry_run: bool = False) -> bool:
    """
    Upload a routine from a JSON file to Hevy.
    
    Args:
        file_path: Path to the routine JSON file
        dry_run: If True, only show what would be done without uploading
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            routine_data = json.load(f)
        
        routine_title = routine_data.get('routine', {}).get('title', 'Unknown')
        print(f"\n📋 Routine: {routine_title}")
        
        # Count exercises
        exercises = routine_data.get('routine', {}).get('exercises', [])
        print(f"   Exercises: {len(exercises)}")
        
        if dry_run:
            print("   [DRY RUN] Would upload this routine")
            return True
        
        # Initialize client
        client = HevyAPIClient()
        
        # Upload routine
        print("   Uploading...")
        response = client.create_routine(routine_data)
        
        # Handle different response formats
        routine_id = None
        if isinstance(response, dict):
            # Check if response has routine key with list
            if 'routine' in response and isinstance(response['routine'], list):
                routine_id = response['routine'][0].get('id') if response['routine'] else None
            else:
                routine_id = response.get('id') or response.get('routine', {}).get('id')
        
        if routine_id:
            print(f"   ✅ Successfully created! Routine ID: {routine_id}")
        else:
            print(f"   ✅ Successfully created!")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Error: File not found - {file_path}")
        return False
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON in file - {file_path}")
        return False
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("   Please set the HEVY_API_KEY environment variable.")
        return False
    except Exception as e:
        print(f"❌ Error uploading routine: {e}")
        return False


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Upload routine JSON files to Hevy API"
    )
    parser.add_argument(
        "file",
        help="Path to routine JSON file or directory containing routines"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without uploading"
    )
    
    args = parser.parse_args()
    
    path = Path(args.file)
    
    if not path.exists():
        print(f"❌ Path not found: {args.file}")
        sys.exit(1)
    
    files_to_upload = []
    
    if path.is_file():
        files_to_upload = [path]
    elif path.is_dir():
        files_to_upload = list(path.glob("*.json"))
    
    if not files_to_upload:
        print("❌ No JSON files found")
        sys.exit(1)
    
    print(f"Found {len(files_to_upload)} routine(s) to upload")
    
    successful = 0
    failed = 0
    
    for file_path in files_to_upload:
        if upload_routine_from_file(str(file_path), dry_run=args.dry_run):
            successful += 1
        else:
            failed += 1
    
    print(f"\n📊 Summary: {successful} successful, {failed} failed")
    
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
