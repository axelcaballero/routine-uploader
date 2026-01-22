"""
Fix Rest Times in Uploaded Routines

Problem: Uploaded routines have incorrect rest_seconds values (120 instead of 60)
Solution: Update all routines via Hevy API with corrected rest_seconds

Rules (from manifesto.md and ROUTINE_CREATION_RULES.md):
- Default: 60 seconds
- Supersets: 0 for all except last (120 seconds)
- Sistema bulgaro with "10-30seg": 30 seconds
- Notes with "10-20seg. de recuperación": 20 seconds
- Core routines: 20 seconds
"""

import json
import time
from hevy_api_client import HevyAPIClient

# Initialize API client
client = HevyAPIClient()

# Routine IDs from HSF 13 folder (December upload)
# Only the first 6 that failed
ROUTINE_IDS = [
    "250cb865-39f7-4442-b098-6ba032d1835b",  # Día 1 – Pecho y Hombro
    "3ebde1c2-9b87-49a1-a76c-3cfbcc3511a5",  # Día 2 – Espalda
    "e4e4da13-721f-4958-b352-037b51883f10",  # Día 3 – Pierna
    "28e3664c-9068-4785-b13c-bb3ac61f55c1",  # Día 4 – Bíceps y Tríceps
    "a7c7d91f-d8f9-4b6f-a1b2-cb805e846761",  # Día 5 – Hombro y Pecho
    "70c7dd1c-fdfe-4fa2-9113-cbf5c4cf99c0",  # Día 6 – Pierna
]


def determine_rest_seconds(exercise, is_core_routine=False):
    """
    Determine correct rest_seconds based on rules
    
    Args:
        exercise: Exercise object with notes and superset_id
        is_core_routine: Boolean indicating if this is a core routine
    
    Returns:
        int: Correct rest_seconds value
    """
    notes = exercise.get('notes', '').lower()
    
    # Core routines: 20 seconds
    if is_core_routine:
        return 20
    
    # Check for special rest time notes
    if '10-20seg' in notes or '10-20 seg' in notes:
        return 20
    
    if 'sistema bulgaro' in notes or 'búlgaro' in notes:
        if '10-30seg' in notes or '10-30 seg' in notes:
            return 30
    
    # Supersets: handled by caller (0 for all except last)
    # This function returns the "last exercise" rest time
    if exercise.get('superset_id'):
        return 120  # Last exercise in superset
    
    # Default
    return 60


def fix_routine_rest_times(routine_id):
    """
    Fetch routine, fix rest times, and update via API
    """
    print(f"\n{'='*60}")
    print(f"Processing routine: {routine_id}")
    print(f"{'='*60}")
    
    # Fetch current routine
    response = client.get_routine(routine_id)
    
    if not response:
        print(f"❌ Failed to fetch routine {routine_id}")
        return False
    
    # Extract routine from response
    routine = response.get('routine', {})
    
    title = routine.get('title', 'Unknown')
    print(f"📋 Routine: {title}")
    
    is_core = 'core' in title.lower()
    if is_core:
        print("🎯 Core routine detected - using 20 second rest times")
    
    exercises = routine.get('exercises', [])
    print(f"📝 Found {len(exercises)} exercises")
    
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
        
        # Remove fields that aren't allowed in PUT requests
        exercise.pop('index', None)
        exercise.pop('title', None)
        
        # Clean sets
        for set_obj in exercise.get('sets', []):
            set_obj.pop('index', None)
        
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
            print(f"  ✏️  Exercise {idx+1}: {old_rest}s → {new_rest}s")
    
    if changes_made == 0:
        print("✅ No changes needed - all rest times already correct")
        return True
    
    print(f"\n📊 Total changes: {changes_made}")
    
    # Update routine via API
    print("🔄 Updating routine...")
    
    try:
        # Remove fields not allowed in PUT
        routine.pop('id', None)
        routine.pop('created_at', None)
        routine.pop('updated_at', None)
        routine.pop('folder_id', None)
        
        # Wrap routine in the expected format
        update_data = {"routine": routine}
        success = client.update_routine(routine_id, update_data)
        
        if success:
            print(f"✅ Successfully updated {title}")
            return True
        else:
            print(f"❌ Failed to update {title}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating routine: {e}")
        return False


def main():
    """
    Fix rest times for all 12 routines
    """
    print("🚀 Starting Rest Time Fix")
    print(f"📅 Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Routines to process: {len(ROUTINE_IDS)}")
    
    results = {
        'success': 0,
        'failed': 0,
        'unchanged': 0
    }
    
    for routine_id in ROUTINE_IDS:
        try:
            success = fix_routine_rest_times(routine_id)
            
            if success:
                results['success'] += 1
            else:
                results['failed'] += 1
                
        except Exception as e:
            print(f"❌ Unexpected error processing {routine_id}: {e}")
            results['failed'] += 1
        
        # Rate limiting: 5 seconds between requests (increased to avoid 429)
        print("⏳ Waiting 5 seconds...")
        time.sleep(5)
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    print(f"✅ Successfully updated: {results['success']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"📝 Total processed: {len(ROUTINE_IDS)}")
    print("="*60)
    
    if results['failed'] == 0:
        print("🎉 All routines updated successfully!")
    else:
        print("⚠️  Some routines failed to update. Review errors above.")


if __name__ == "__main__":
    main()
