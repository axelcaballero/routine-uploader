"""
Fix rest_seconds in local JSON files before upload

Corrects rest times according to ROUTINE_CREATION_RULES.md:
- Default: 60 seconds
- Supersets: 0 for all except last (120 seconds)
- Special cases based on notes
"""

import json
import re
from pathlib import Path


def determine_rest_seconds(exercise, is_core_routine=False):
    """
    Determine correct rest_seconds based on rules
    """
    notes = exercise.get('notes', '').lower()
    
    # Core routines: 20 seconds
    if is_core_routine:
        return 20
    
    # Check for special rest time notes
    if '10-20seg' in notes or '10-20 seg' in notes:
        return 20
    
    if 'sistema bulgaro' in notes or 'búlgaro' in notes or 'bulgaro' in notes:
        if '10-30seg' in notes or '10-30 seg' in notes:
            return 30
    
    # Supersets handled by caller
    if exercise.get('superset_id'):
        return 120  # Placeholder for last exercise
    
    # Default
    return 60


def fix_routine_file(file_path):
    """
    Fix rest times in a single routine JSON file
    """
    print(f"\n{'='*60}")
    print(f"Processing: {file_path.name}")
    print(f"{'='*60}")
    
    # Load routine
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    routine = data.get('routine', {})
    title = routine.get('title', 'Unknown')
    exercises = routine.get('exercises', [])
    
    print(f"📋 {title}")
    print(f"🏋️  {len(exercises)} exercises")
    
    is_core = 'core' in title.lower()
    if is_core:
        print("🎯 Core routine detected")
    
    # Track changes
    changes_made = 0
    
    # Group exercises by superset
    superset_groups = {}
    for idx, exercise in enumerate(exercises):
        superset_id = exercise.get('superset_id')
        if superset_id:
            if superset_id not in superset_groups:
                superset_groups[superset_id] = []
            superset_groups[superset_id].append(idx)
    
    # Fix rest times
    for idx, exercise in enumerate(exercises):
        old_rest = exercise.get('rest_seconds', 60)
        
        # Determine correct rest time
        if exercise.get('superset_id'):
            superset_id = exercise['superset_id']
            # Check if this is the last exercise in the superset
            if idx == superset_groups[superset_id][-1]:
                new_rest = 120  # Last in superset
            else:
                new_rest = 0  # Not last in superset
        else:
            new_rest = determine_rest_seconds(exercise, is_core)
        
        # Update if different
        if old_rest != new_rest:
            exercise['rest_seconds'] = new_rest
            changes_made += 1
            notes_preview = exercise.get('notes', '')[:50]
            print(f"  ✏️  Exercise {idx+1} ({notes_preview}...): {old_rest}s → {new_rest}s")
    
    if changes_made == 0:
        print("✅ No changes needed")
        return False
    
    print(f"\n📊 Total changes: {changes_made}")
    
    # Save updated file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved: {file_path}")
    
    return True


def main():
    """
    Fix rest times in all December routine JSON files
    """
    print("🚀 Fixing Local Rest Times")
    print("="*60)
    
    input_dir = Path(__file__).parent / 'input'
    files = sorted(input_dir.glob('dia_*_dic.json'))
    
    if not files:
        print("❌ No dia_*_dic.json files found in input/")
        return
    
    print(f"📁 Found {len(files)} files to process\n")
    
    results = {
        'modified': 0,
        'unchanged': 0
    }
    
    for file_path in files:
        modified = fix_routine_file(file_path)
        
        if modified:
            results['modified'] += 1
        else:
            results['unchanged'] += 1
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    print(f"✏️  Modified: {results['modified']}")
    print(f"✅ Unchanged: {results['unchanged']}")
    print(f"📝 Total: {len(files)}")
    print("="*60)
    
    if results['modified'] > 0:
        print("\n🎉 Files updated! Ready to upload with correct rest times.")
        print("\nNext step: Upload routines")
        print("  python batch_routine_uploader.py --batch-file input/dia_*_dic.json --folder-id 1986567")
    else:
        print("\n✅ All files already have correct rest times!")


if __name__ == "__main__":
    main()
