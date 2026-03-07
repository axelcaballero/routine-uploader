#!/Users/axelcaballero/projects/hevy/routine-uploader/venv/bin/python
"""
Batch Routine Uploader - Safely handles importing multiple routines from external sources.

Designed to work with routine-extractor project output, with safeguards for bulk operations.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from hevy_api_client import HevyAPIClient
from routine_enhancer import RoutineEnhancer
from exercise_validator import ExerciseValidator


class BatchRoutineUploader:
    """Handles bulk routine uploads with validation and safety checks."""
    
    def __init__(self, api_client=None, session_folder_title: Optional[str] = None):
        self.client = api_client or HevyAPIClient()
        self.validator = ExerciseValidator()
        self.enhancer = RoutineEnhancer(api_client=self.client)
        self.session_folder_title = session_folder_title.strip() if session_folder_title else None
        self.session_folder_id = None

        if self.session_folder_title:
            self.session_folder_id = self.client.ensure_routine_folder_id(self.session_folder_title)
            if not self.session_folder_id:
                raise Exception(f"Session folder '{self.session_folder_title}' has no ID")
            print(f"📁 Session upload folder verified: {self.session_folder_title} (ID: {self.session_folder_id})")

    def _apply_session_folder(self, routine_data: Dict):
        """Apply session folder ID to a routine payload when this session configured one."""
        routine = routine_data.get("routine")
        if isinstance(routine, dict) and self.session_folder_id is not None:
            routine["folder_id"] = self.session_folder_id
    
    def _validate_structure(self, routine_data: Dict, errors: List[str]):
        """Inline structure validation."""
        # Check root "routine" key
        if "routine" not in routine_data:
            errors.append("Structure: Missing root 'routine' key")
            return
        
        routine = routine_data["routine"]
        
        # Required fields
        if "title" not in routine:
            errors.append("Structure: Missing 'title'")
        if "exercises" not in routine or not routine["exercises"]:
            errors.append("Structure: Missing or empty 'exercises'")
            return
        
        # Validate each exercise
        for j, exercise in enumerate(routine["exercises"], 1):
            if "exercise_template_id" not in exercise:
                errors.append(f"Structure: Exercise {j} missing 'exercise_template_id'")
            elif not exercise["exercise_template_id"]:
                errors.append(f"Structure: Exercise {j} has empty 'exercise_template_id'")
            
            if "sets" not in exercise or not exercise["sets"]:
                errors.append(f"Structure: Exercise {j} missing or empty 'sets'")
                continue
            
            # Validate set types
            valid_types = ["warmup", "normal", "dropset", "failure"]
            for k, set_data in enumerate(exercise["sets"], 1):
                if "type" not in set_data:
                    errors.append(f"Structure: Exercise {j}, Set {k} missing 'type'")
                elif set_data["type"] not in valid_types:
                    errors.append(f"Structure: Exercise {j}, Set {k} invalid type '{set_data['type']}' (use: {', '.join(valid_types)})")
    
    def load_batch_file(self, file_path: str) -> List[Dict]:
        """
        Load a batch file containing multiple routines.
        
        Expected format:
        {
          "routines": [
            { "routine": { "title": "Día 1 – ...", "exercises": [...] } },
            { "routine": { "title": "Día 2 – ...", "exercises": [...] } }
          ]
        }
        
        Or single routine format (will be wrapped in array).
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different input formats
        if 'routines' in data:
            # Batch format
            return data['routines']
        elif 'routine' in data:
            # Single routine format
            return [data]
        else:
            raise ValueError(
                "Invalid format. Expected either:\n"
                '  {"routines": [...]}\n'
                '  {"routine": {...}}'
            )
    
    def validate_batch(self, routines: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Validate all routines before uploading any.
        
        Returns:
            Tuple of (valid_routines, invalid_routines)
        """
        valid = []
        invalid = []
        
        print(f"\n{'='*70}")
        print(f"🔍 VALIDATION PHASE - Checking {len(routines)} routine(s)")
        print(f"{'='*70}\n")
        
        for i, routine_data in enumerate(routines, 1):
            self._apply_session_folder(routine_data)
            routine_title = routine_data.get('routine', {}).get('title', f'Routine {i}')
            print(f"[{i}/{len(routines)}] {routine_title}")
            
            errors = []
            
            # 1. Structure validation (inline - validate_routine_structure expects file path)
            self._validate_structure(routine_data, errors)
            
            # 2. Exercise ID validation
            is_valid, exercise_errors = self.validator.validate_routine(routine_data, verbose=False)
            if not is_valid:
                errors.extend([f"Exercise: {e}" for e in exercise_errors])
            
            # 3. Check for required fields
            if not routine_data.get('routine', {}).get('title'):
                errors.append("Missing routine title")
            if not routine_data.get('routine', {}).get('exercises'):
                errors.append("No exercises defined")
            
            if errors:
                print(f"   ❌ FAILED - {len(errors)} error(s)")
                for error in errors:
                    print(f"      • {error}")
                invalid.append({
                    'routine': routine_data,
                    'errors': errors,
                    'index': i
                })
            else:
                print(f"   ✅ VALID")
                valid.append(routine_data)
        
        return valid, invalid
    
    def upload_batch(
        self,
        routines: List[Dict],
        dry_run: bool = False,
        enhance: bool = True,
        interactive: bool = True
    ) -> Dict:
        """
        Upload multiple routines with progress tracking.
        
        Args:
            routines: List of routine dictionaries
            dry_run: If True, validate but don't upload
            enhance: If True, auto-populate warmup weights
            interactive: If True, require confirmation before uploading
            
        Returns:
            Dict with success/failure counts and details
        """
        results = {
            'successful': [],
            'failed': [],
            'skipped': []
        }
        
        # Validation phase
        valid_routines, invalid_routines = self.validate_batch(routines)
        
        if invalid_routines:
            print(f"\n⚠️  {len(invalid_routines)} routine(s) failed validation")
            print("Fix errors before proceeding.\n")
            results['failed'] = invalid_routines
            return results
        
        if not valid_routines:
            print("\n❌ No valid routines to upload\n")
            return results
        
        print(f"\n✅ All {len(valid_routines)} routine(s) passed validation!")
        if self.session_folder_id is not None:
            print(f"📁 Session folder: {self.session_folder_title} (ID: {self.session_folder_id})")
        else:
            print("📁 Session folder: not overridden (using each routine's folder_id)")
        
        # Interactive confirmation
        if interactive and not dry_run:
            print(f"\n{'='*70}")
            print(f"⚠️  READY TO UPLOAD {len(valid_routines)} ROUTINE(S)")
            print(f"{'='*70}")
            print("\nRoutines to be created:")
            for i, routine in enumerate(valid_routines, 1):
                title = routine.get('routine', {}).get('title', 'Unknown')
                exercise_count = len(routine.get('routine', {}).get('exercises', []))
                print(f"   {i}. {title} ({exercise_count} exercises)")
            
            response = input(f"\nProceed with upload? [y/N]: ").strip().lower()
            if response not in ['y', 'yes']:
                print("\n❌ Upload cancelled by user")
                results['skipped'] = valid_routines
                return results
        
        # Upload phase
        print(f"\n{'='*70}")
        print(f"📤 UPLOAD PHASE - Creating {len(valid_routines)} routine(s)")
        print(f"{'='*70}\n")
        
        for i, routine_data in enumerate(valid_routines, 1):
            self._apply_session_folder(routine_data)
            routine_title = routine_data.get('routine', {}).get('title', f'Routine {i}')
            print(f"[{i}/{len(valid_routines)}] {routine_title}")
            
            try:
                # Enhancement
                if enhance:
                    try:
                        routine_data = self.enhancer.enhance_routine(
                            routine_data,
                            warmup_strategy="recent",
                            verbose=False
                        )
                        print(f"   ✓ Enhanced with historical data")
                    except Exception as e:
                        print(f"   ⚠ Enhancement skipped: {e}")
                
                if dry_run:
                    print(f"   ✓ [DRY RUN] Would upload")
                    results['successful'].append({
                        'title': routine_title,
                        'index': i,
                        'dry_run': True
                    })
                else:
                    # Rate limiting: wait between uploads
                    import time
                    if i > 1:  # Don't wait before first upload
                        time.sleep(2)  # 2 second delay between uploads
                    
                    # Upload
                    response = self.client.create_routine(routine_data)
                    
                    # Extract routine ID
                    routine_id = None
                    if isinstance(response, dict):
                        if 'routine' in response and isinstance(response['routine'], list):
                            routine_id = response['routine'][0].get('id') if response['routine'] else None
                        else:
                            routine_id = response.get('id') or response.get('routine', {}).get('id')
                    
                    print(f"   ✅ Created! ID: {routine_id}")
                    results['successful'].append({
                        'title': routine_title,
                        'id': routine_id,
                        'index': i
                    })
                
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                results['failed'].append({
                    'title': routine_title,
                    'error': str(e),
                    'index': i
                })
        
        return results
    
    def print_summary(self, results: Dict):
        """Print upload summary."""
        print(f"\n{'='*70}")
        print("📊 BATCH UPLOAD SUMMARY")
        print(f"{'='*70}\n")
        
        successful = len(results['successful'])
        failed = len(results['failed'])
        skipped = len(results['skipped'])
        total = successful + failed + skipped
        
        print(f"Total routines: {total}")
        print(f"✅ Successful:  {successful}")
        print(f"❌ Failed:      {failed}")
        print(f"⏭️  Skipped:     {skipped}")
        
        if results['successful']:
            print(f"\n✅ Successfully uploaded:")
            for item in results['successful']:
                if item.get('dry_run'):
                    print(f"   [{item['index']}] {item['title']} [DRY RUN]")
                else:
                    print(f"   [{item['index']}] {item['title']} (ID: {item.get('id', 'N/A')})")
        
        if results['failed']:
            print(f"\n❌ Failed uploads:")
            for item in results['failed']:
                print(f"   [{item['index']}] {item['title']}")
                print(f"      Error: {item.get('error', 'Unknown')}")
        
        if results['skipped']:
            print(f"\n⏭️  Skipped (validation errors or user cancelled):")
            for item in results['skipped']:
                if isinstance(item, dict) and 'errors' in item:
                    print(f"   [{item['index']}] {item['routine'].get('routine', {}).get('title', 'Unknown')}")
                else:
                    print(f"   {item.get('routine', {}).get('title', 'Unknown')}")
        
        print()


def main():
    """Main entry point for batch routine uploader."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Batch upload multiple routines from routine-extractor output",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate only (dry run)
  %(prog)s extracted_routines.json --dry-run

    # Validate/upload using a session folder (create if missing)
    %(prog)s extracted_routines.json --folder-title "HSF 15"
  
  # Upload with confirmation prompt
  %(prog)s extracted_routines.json
  
  # Upload without confirmation (careful!)
  %(prog)s extracted_routines.json --no-interactive
  
  # Upload without enhancement
  %(prog)s extracted_routines.json --no-enhance
  
Input format:
  Batch format (multiple routines):
    {
      "routines": [
        { "routine": { "title": "Día 1 – ...", ... } },
        { "routine": { "title": "Día 2 – ...", ... } }
      ]
    }
  
  Single routine format (also accepted):
    { "routine": { "title": "Día 1 – ...", ... } }
        """
    )
    
    parser.add_argument('file', help='JSON file containing routines')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Validate without uploading')
    parser.add_argument('--no-enhance', action='store_true',
                       help='Skip warmup weight enhancement')
    parser.add_argument('--no-interactive', action='store_true',
                       help='Skip confirmation prompt (auto-upload)')
    parser.add_argument('--folder-title', type=str,
                       help='Session folder title for this run (finds or creates folder and applies to all routines)')
    
    args = parser.parse_args()
    
    # Validate file exists
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ File not found: {args.file}")
        sys.exit(1)
    
    try:
        # Initialize uploader
        uploader = BatchRoutineUploader(session_folder_title=args.folder_title)
        
        # Load routines
        print(f"📂 Loading routines from: {args.file}")
        routines = uploader.load_batch_file(args.file)
        print(f"   Found {len(routines)} routine(s)\n")
        
        # Upload
        results = uploader.upload_batch(
            routines,
            dry_run=args.dry_run,
            enhance=not args.no_enhance,
            interactive=not args.no_interactive
        )
        
        # Print summary
        uploader.print_summary(results)
        
        # Exit code based on results
        if results['failed']:
            sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
