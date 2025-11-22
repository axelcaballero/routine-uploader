#!/usr/bin/env python3
"""
Determine the next workout based on recent activity and routine sequence.

Step-by-step process:
1. Get latest workout from /v1/workouts
2. Extract routine_id from latest workout
3. Get routine details to extract folder_id
4. Fetch all routines and filter by folder_id
5. Extract día numbers from routine titles
6. Find next routine by día number
"""

import sys
import os
import json
import re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hevy_api_client import HevyAPIClient
from typing import Optional, Dict, Any, List


def get_most_recent_workout(client: HevyAPIClient) -> Optional[Dict[str, Any]]:
    """Get the most recent completed workout from /v1/workouts."""
    workouts = client.list_workouts(page=1, page_size=1)
    workouts_list = workouts.get('workouts', [])
    
    if not workouts_list:
        return None
    
    return workouts_list[0]


def extract_dia_number(routine_title: str) -> Optional[int]:
    """Extract the día number from a routine title."""
    match = re.search(r'Día\s*(\d+)', routine_title, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def get_routines_in_folder(client: HevyAPIClient, folder_id: int) -> List[Dict[str, Any]]:
    """Fetch all routines and filter by folder_id."""
    all_routines = []
    page = 1
    
    while True:
        response = client.list_routines(page=page, page_size=10)
        routines_page = response.get('routines', [])
        all_routines.extend(routines_page)
        
        if page >= response.get('page_count', 1):
            break
        page += 1
    
    # Filter by folder_id and extract día numbers
    folder_routines = []
    for routine in all_routines:
        if routine.get('folder_id') == folder_id:
            dia_number = extract_dia_number(routine.get('title', ''))
            if dia_number:
                routine['dia_number'] = dia_number
                folder_routines.append(routine)
    
    return folder_routines


def get_next_routine(folder_routines: List[Dict[str, Any]], current_dia: int) -> Optional[Dict[str, Any]]:
    """Find next routine by día number."""
    # Sort by día number
    sorted_routines = sorted(folder_routines, key=lambda x: x.get('dia_number', 0))
    
    # Find routines with día > current_dia
    next_routines = [r for r in sorted_routines if r.get('dia_number', 0) > current_dia]
    
    # If found, return the next one; otherwise wrap around to first
    if next_routines:
        return next_routines[0]
    else:
        return sorted_routines[0] if sorted_routines else None


def display_next_workout(client: HevyAPIClient, routine: Dict[str, Any]) -> None:
    """Display the next workout details."""
    routine_id = routine.get('id')
    full_routine = client.get_routine(routine_id)
    routine_data = full_routine.get('routine', {})
    
    print("\n" + "="*66)
    print("YOUR NEXT WORKOUT")
    print("="*66)
    print(f"\n📅 Routine: {routine_data.get('title')}")
    print(f"💪 Total Exercises: {len(routine_data.get('exercises', []))}")
    
    print("\nExercises:")
    total_sets = 0
    for idx, exercise in enumerate(routine_data.get('exercises', []), 1):
        title = exercise.get('title', 'Unknown')
        sets = exercise.get('sets', [])
        normal_sets = [s for s in sets if s.get('type') == 'normal']
        reps = normal_sets[0].get('reps', '?') if normal_sets else '?'
        
        total_sets += len(normal_sets)
        
        notes = exercise.get('notes', '')
        notes_str = f" - {notes}" if notes else ""
        
        print(f"  {idx}. {title} ({reps} reps) ({len(normal_sets)} sets){notes_str}")
    
    print(f"\nTotal: {total_sets} sets")


def save_next_workout_info(next_routine: Dict[str, Any]) -> None:
    """Save next workout information for future reference."""
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'next_workout.json')
    
    next_workout_info = {
        'routine_id': next_routine.get('id'),
        'title': next_routine.get('title'),
        'dia_number': next_routine.get('dia_number'),
        'folder_id': next_routine.get('folder_id')
    }
    
    with open(output_file, 'w') as f:
        json.dump(next_workout_info, f, indent=2)
    
    print(f"✅ Next workout saved to data/next_workout.json")


def main():
    """Main function to determine and display next workout."""
    client = HevyAPIClient()
    
    try:
        print("Connected to Hevy API")
        print("Fetching most recent workout...")
        
        # Step 1: Get latest workout
        latest_workout = get_most_recent_workout(client)
        if not latest_workout:
            print("No workouts found")
            return
        
        latest_title = latest_workout.get('title')
        latest_routine_id = latest_workout.get('routine_id')
        current_dia = extract_dia_number(latest_title)
        
        print(f"Most recent: {latest_title} (Día {current_dia})")
        
        # Step 2-3: Get routine details to extract folder_id
        print("Getting routine folder...")
        current_routine = client.get_routine(latest_routine_id)
        folder_id = current_routine.get('routine', {}).get('folder_id')
        
        if not folder_id:
            print("Could not determine routine folder")
            return
        
        print(f"Folder ID: {folder_id}")
        
        # Step 4-5: Fetch routines in folder and extract día numbers
        print("Fetching all routines in folder...")
        folder_routines = get_routines_in_folder(client, folder_id)
        print(f"Found {len(folder_routines)} routines in folder")
        
        # Step 6: Find next routine
        print("Finding next workout in sequence...")
        next_routine = get_next_routine(folder_routines, current_dia)
        
        if next_routine:
            display_next_workout(client, next_routine)
            save_next_workout_info(next_routine)
        else:
            print("Could not find next routine in sequence")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
