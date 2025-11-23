#!/Users/axelcaballero/projects/hevy/routine-uploader/venv/bin/python
"""
Script to upload routine JSON files to Hevy API.
"""

import json
import sys
from pathlib import Path
from hevy_api_client import HevyAPIClient
from routine_enhancer import RoutineEnhancer
from exercise_validator import ExerciseValidator


def upload_routine_from_file(
    file_path: str,
    dry_run: bool = False,
    enhance: bool = True,
    warmup_strategy: str = "recent",
    validate: bool = True
) -> bool:
    """
    Upload a routine from a JSON file to Hevy.
    
    Args:
        file_path: Path to the routine JSON file
        dry_run: If True, only show what would be done without uploading
        enhance: If True, auto-populate warmup weights from history
        warmup_strategy: Strategy for warmup weight ("recent", "average", "mode")
        validate: If True, validate exercise IDs against instructions.md
        
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
        
        # Validate exercise IDs against instructions.md
        if validate:
            print("   Validating exercise IDs...")
            validator = ExerciseValidator()
            is_valid, errors = validator.validate_routine(routine_data, verbose=False)
            if not is_valid:
                print(f"   ❌ Validation failed: {len(errors)} exercise(s) not found in instructions.md")
                for error in errors:
                    print(f"      {error}")
                print("   Use: python exercise_validator.py --list  to see available exercises")
                return False
            print("   ✓ All exercise IDs valid")
        
        # Enhance routine with warmup data from history
        if enhance:
            print("   Enhancing with historical warmup data...")
            try:
                client = HevyAPIClient()
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
        help="Skip exercise ID validation against instructions.md"
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
        if upload_routine_from_file(
            str(file_path),
            dry_run=args.dry_run,
            enhance=not args.no_enhance,
            warmup_strategy=args.warmup_strategy,
            validate=not args.no_validate
        ):
            successful += 1
        else:
            failed += 1
    
    print(f"\n📊 Summary: {successful} successful, {failed} failed")
    
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
