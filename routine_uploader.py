#!/usr/bin/env python3
"""
Routine upload workflow for the Hevy Training Toolkit.
"""

import json
import sys
from pathlib import Path
from typing import Any, Optional
from hevy_api_client import HevyAPIClient
from routine_enhancer import RoutineEnhancer
from scripts.exercise_validator import ExerciseValidator


def upload_routine_from_file(
    file_path: str,
    dry_run: bool = False,
    enhance: bool = True,
    warmup_strategy: str = "recent",
    validate: bool = True,
    session_folder_title: Optional[str] = None,
    session_folder_id: Optional[Any] = None,
    api_client: Optional[HevyAPIClient] = None,
) -> bool:
    """
    Upload a routine from a JSON file to Hevy.
    
    Args:
        file_path: Path to the routine JSON file
        dry_run: If True, only show what would be done without uploading
        enhance: If True, auto-populate warmup weights from history
        warmup_strategy: Strategy for warmup weight ("recent", "average", "mode")
        validate: If True, validate exercise IDs against exercise_mappings.md
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            routine_data = json.load(f)

        client = api_client or HevyAPIClient()

        # Apply session folder only when explicitly provided
        if session_folder_title:
            resolved_folder_id = session_folder_id
            if resolved_folder_id is None:
                resolved_folder_id = client.ensure_routine_folder_id(session_folder_title)
            routine_data.setdefault('routine', {})['folder_id'] = resolved_folder_id
        
        routine_title = routine_data.get('routine', {}).get('title', 'Unknown')
        print(f"\n📋 Routine: {routine_title}")
        if session_folder_title:
            print(f"   Session Folder: {session_folder_title} (ID: {routine_data.get('routine', {}).get('folder_id')})")
        else:
            existing_folder_id = routine_data.get('routine', {}).get('folder_id')
            if existing_folder_id is None:
                print("   ⚠ Folder ID: not set in file (use --folder-title to set for this session)")
            else:
                print(f"   Folder ID (from file): {existing_folder_id}")
        
        # Count exercises
        exercises = routine_data.get('routine', {}).get('exercises', [])
        print(f"   Exercises: {len(exercises)}")
        
        # Validate exercise IDs against exercise_mappings.md
        if validate:
            print("   Validating exercise IDs...")
            validator = ExerciseValidator()
            is_valid, errors = validator.validate_routine(routine_data, verbose=False)
            if not is_valid:
                print(f"   ❌ Validation failed: {len(errors)} exercise(s) not found in exercise_mappings.md")
                for error in errors:
                    print(f"      {error}")
                print("   Use: python exercise_validator.py --list  to see available exercises")
                return False
            print("   ✓ All exercise IDs valid")
        
        # Enhance routine with warmup data from history
        if enhance:
            print("   Enhancing with historical warmup data...")
            try:
                enhancer = RoutineEnhancer(api_client=client)
                routine_data = enhancer.enhance_routine(
                    routine_data,
                    warmup_strategy=warmup_strategy,
                    verbose=False
                )
                print("   ✓ Enhancement complete")
            except Exception as e:
                print(f"   ⚠ Enhancement skipped: {e}")
                # Continue with original data if enhancement fails
        
        if dry_run:
            print("   [DRY RUN] Would upload this routine")
            return True
        
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
    parser.add_argument(
        "--no-enhance",
        action="store_true",
        help="Skip automatic warmup weight population"
    )
    parser.add_argument(
        "--warmup-strategy",
        choices=["recent", "average", "mode"],
        default="recent",
        help="Strategy for choosing warmup weight (default: recent)"
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip exercise ID validation against exercise_mappings.md"
    )
    parser.add_argument(
        "--folder-title",
        type=str,
        help="Session folder title for this run (finds or creates folder, then assigns it to all uploads)"
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

    shared_client = None
    session_folder_title = args.folder_title.strip() if args.folder_title else None
    session_folder_id = None

    if session_folder_title:
        try:
            shared_client = HevyAPIClient()
            session_folder_id = shared_client.ensure_routine_folder_id(session_folder_title)
            print(f"📁 Session upload folder verified: {session_folder_title} (ID: {session_folder_id})")
        except Exception as e:
            print(f"❌ Failed to verify/create session folder '{session_folder_title}': {e}")
            sys.exit(1)
    
    print(f"Found {len(files_to_upload)} routine(s) to upload")
    
    successful = 0
    failed = 0
    
    for file_path in files_to_upload:
        if upload_routine_from_file(
            str(file_path),
            dry_run=args.dry_run,
            enhance=not args.no_enhance,
            warmup_strategy=args.warmup_strategy,
            validate=not args.no_validate,
            session_folder_title=session_folder_title,
            session_folder_id=session_folder_id,
            api_client=shared_client
        ):
            successful += 1
        else:
            failed += 1
    
    print(f"\n📊 Summary: {successful} successful, {failed} failed")
    
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
