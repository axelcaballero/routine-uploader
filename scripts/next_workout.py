#!/usr/bin/env python3
"""
Determine the next workout based on recent activity and routine sequence.

Step-by-step process:
1. Get latest workout from /v1/workouts
2. Extract routine_id from latest workout
3. Get routine details to extract folder_id
4. Fetch all routines and filter by folder_id
5. Extract day numbers from routine titles
6. Find next routine by day number
7. Estimate duration from workout history
"""

import sys
import os
import json
import re
import unicodedata
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hevy_api_client import HevyAPIClient
from typing import Optional, Dict, Any, List


def _normalize_workout_title(value: str) -> str:
    """Normalize title for comparison."""
    normalized = unicodedata.normalize("NFKD", value.casefold())
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", ascii_text).strip()


def _parse_additional_training_schedule(file_path: str) -> Dict[int, Dict[str, Any]]:
    """Load additional training configuration from docs/additional-traning.md."""
    schedule: Dict[int, Dict[str, Any]] = {}

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for raw_line in f:
                line = raw_line.strip()
                match = re.match(r'^\*\s*Day\s+(\d+)\s+[^,]+(?:,\s*(.+?))?\.?$', line, flags=re.IGNORECASE)
                if not match:
                    continue

                day_number = int(match.group(1))
                details = (match.group(2) or '').strip()
                normalized = _normalize_workout_title(details)

                cardio_minutes: Optional[int] = None
                cardio_match = re.search(r'(\d+)\s*minutes?\s*cardio', normalized)
                if cardio_match:
                    cardio_minutes = int(cardio_match.group(1))

                schedule[day_number] = {
                    'calves': 'calves' in normalized,
                    'forearms': 'forearms' in normalized,
                    'core': 'core' in normalized,
                    'cardio_minutes': cardio_minutes,
                    'notes': details,
                }
    except FileNotFoundError:
        print(f"Warning: {file_path} not found. Additional training notes will be omitted.")

    return schedule


def _format_duration_minutes(total_minutes: int) -> str:
    """Convert minutes into hours/minutes string."""
    hours = total_minutes // 60
    minutes = total_minutes % 60
    if hours:
        return f"{hours}h {minutes}m" if minutes else f"{hours}h"
    return f"{minutes}m"


def _build_additional_training_summary(day_number: Optional[int]) -> Optional[Dict[str, Any]]:
    """Build additional training details for the given routine day."""
    if day_number is None:
        return None

    schedule_file = os.path.join(os.path.dirname(__file__), '..', 'docs', 'additional-traning.md')
    schedule = _parse_additional_training_schedule(schedule_file)
    info = schedule.get(day_number)
    if not info:
        return None

    targeted: List[str] = []
    extra_minutes = 0
    if info.get('calves'):
        targeted.append('calves')
        extra_minutes += 15
    if info.get('forearms'):
        targeted.append('forearms')
        extra_minutes += 15
    if info.get('core'):
        extra_minutes += 15

    cardio_minutes = info.get('cardio_minutes') or 0
    extra_minutes += cardio_minutes

    if not targeted and not info.get('core') and cardio_minutes == 0:
        return None

    return {
        'targeted': targeted,
        'core': info.get('core', False),
        'cardio_minutes': cardio_minutes,
        'total_minutes': extra_minutes,
        'notes': info.get('notes', ''),
    }


def _is_allowed_main_workout_title(title: str) -> bool:
    """Check if title is a main muscle group workout (Day 1-6, excluding core/forearms/calves)."""
    normalized = _normalize_workout_title(title)
    
    # Only include Day/Dia 1-6
    day_match = re.search(r"\b(?:day|dia)\s*([1-6])\b", normalized)
    if not day_match:
        return False
    
    # Exclude core, forearms, calves
    excluded_tokens = (
        "core", "abs", "abdominal", "forearm", "forearms",
        "antebrazo", "antebrazos", "calf", "calves",
        "pantorrilla", "pantorrillas", "gemelo", "gemelos",
    )
    return not any(token in normalized for token in excluded_tokens)


def get_most_recent_workout(client: HevyAPIClient) -> Optional[Dict[str, Any]]:
    """Get the most recent qualifying (Day 1-6) completed workout from /v1/workouts."""
    page = 1
    while True:
        workouts = client.list_workouts(page=page, page_size=10)
        workouts_list = workouts.get('workouts', [])
        
        if not workouts_list:
            return None
        
        for workout in workouts_list:
            title = str(workout.get('title', ''))
            if _is_allowed_main_workout_title(title):
                return workout
        
        if len(workouts_list) < 10:
            return None
        page += 1


def extract_day_number(routine_title: str) -> Optional[int]:
    """Extract the day number from a Spanish or English routine title."""
    match = re.search(r'(?:día|dia|day)\s*(\d+)', routine_title, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def get_routines_in_folder(client: HevyAPIClient, folder_id: int) -> List[Dict[str, Any]]:
    """Fetch all routines and filter by folder_id and allowed main workouts only."""
    all_routines = []
    page = 1
    
    while True:
        response = client.list_routines(page=page, page_size=10)
        routines_page = response.get('routines', [])
        all_routines.extend(routines_page)
        
        if page >= response.get('page_count', 1):
            break
        page += 1
    
    # Filter by folder_id, allowed titles (Day 1-6, no core/forearms/calves), and extract day numbers
    folder_routines = []
    for routine in all_routines:
        if routine.get('folder_id') == folder_id:
            title = str(routine.get('title', ''))
            if _is_allowed_main_workout_title(title):
                day_number = extract_day_number(title)
                if day_number:
                    routine['day_number'] = day_number
                    folder_routines.append(routine)
    
    return folder_routines


def get_next_routine(folder_routines: List[Dict[str, Any]], current_day: int) -> Optional[Dict[str, Any]]:
    """Find next routine by day number."""
    # Sort by day number
    sorted_routines = sorted(folder_routines, key=lambda x: x.get('day_number', 0))
    
    # Find routines with day number > current_day
    next_routines = [r for r in sorted_routines if r.get('day_number', 0) > current_day]
    
    # If found, return the next one; otherwise wrap around to first
    if next_routines:
        return next_routines[0]
    else:
        return sorted_routines[0] if sorted_routines else None


def get_estimated_duration(client: HevyAPIClient, routine_id: str) -> Optional[int]:
    """Get estimated workout duration in minutes based on historical data for the same routine."""
    try:
        all_workouts = []
        page = 1
        while True:
            workouts = client.list_workouts(page=page, page_size=10)
            workouts_list = workouts.get('workouts', [])
            if not workouts_list:
                break
            all_workouts.extend(workouts_list)
            if page >= workouts.get('page_count', 1):
                break
            page += 1
        
        # Find workouts with matching routine_id and duration
        durations = []
        for workout in all_workouts:
            if workout.get('routine_id') == routine_id:
                workout_id = workout.get('id')
                full_workout = client.get_workout(workout_id)
                start = full_workout.get('start_time')
                end = full_workout.get('end_time')
                
                if start and end:
                    s = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    e = datetime.fromisoformat(end.replace('Z', '+00:00'))
                    dur = e - s
                    durations.append(int(dur.total_seconds()))
        
        if durations:
            avg_seconds = sum(durations) // len(durations)
            return avg_seconds // 60
    
    except Exception:
        pass
    
    return None


def display_next_workout(client: HevyAPIClient, routine: Dict[str, Any]) -> None:
    """Display the next workout details in readable format."""
    routine_id = routine.get('id')
    full_routine = client.get_routine(routine_id)
    routine_data = full_routine.get('routine', {})
    day_number = extract_day_number(routine_data.get('title', ''))
    additional_info = _build_additional_training_summary(day_number)
    
    print(f"\n📅 Routine: {routine_data.get('title')}")
    print(f"💪 Total Exercises: {len(routine_data.get('exercises', []))}")
    
    estimated_main_minutes = get_estimated_duration(client, routine_id)
    if estimated_main_minutes is not None:
        print(f"⏱️  Main workout duration: {_format_duration_minutes(estimated_main_minutes)}")
    else:
        print("⏱️  Main workout duration: unavailable")

    if additional_info:
        print("\n🧩 Additional training:")
        if additional_info['targeted']:
            targeted_text = ', '.join([f"{muscle} (15m)" for muscle in additional_info['targeted']])
            print(f"  • Targeted: {targeted_text}")
        if additional_info['core']:
            print("  • Core: 15m")
        if additional_info['cardio_minutes']:
            print(f"  • Cardio: {_format_duration_minutes(additional_info['cardio_minutes'])}")
        print(f"  • Additional training time: {_format_duration_minutes(additional_info['total_minutes'])}")

    combined_minutes = (estimated_main_minutes or 0) + (additional_info['total_minutes'] if additional_info else 0)
    print(f"\n🔗 Combined training time: {_format_duration_minutes(combined_minutes)}")

    print("\nExercises:")
    for idx, exercise in enumerate(routine_data.get('exercises', []), 1):
        title = exercise.get('title', 'Unknown')
        sets = exercise.get('sets', [])
        normal_sets = [s for s in sets if s.get('type') == 'normal']
        notes = exercise.get('notes', '')
        
        # Get reps from first normal set
        reps = normal_sets[0].get('reps', '?') if normal_sets else '?'
        set_count = len(normal_sets)
        
        print(f"  {idx}. {title}")
        print(f"     Reps: {reps} × {set_count} sets")
        
        # Only show notes if they contain useful descriptive info
        if notes:
            filtered_notes = notes
            # Remove rep scheme patterns (e.g., "4x6-8rep.", "3x20rep.", etc.)
            filtered_notes = re.sub(r'\d+x\d+(?:-\d+)?rep\.?', '', filtered_notes)
            # Remove percentages and effort indicators
            filtered_notes = re.sub(r'\s*\(.*?\)', '', filtered_notes)
            filtered_notes = re.sub(r'\s+o\s+más', '', filtered_notes)
            filtered_notes = re.sub(r'\s*\d+%\+?', '', filtered_notes)
            filtered_notes = filtered_notes.strip()
            
            # Only display if there's meaningful content left
            if filtered_notes and len(filtered_notes) > 2:
                print(f"     Notes: {filtered_notes}")


def save_next_workout_info(client: HevyAPIClient, next_routine: Dict[str, Any]) -> None:
    """Save next workout information for future reference."""
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(output_dir, exist_ok=True)
    
    day_number = next_routine.get('day_number')
    additional_info = _build_additional_training_summary(day_number)
    estimated_main_minutes = get_estimated_duration(client, next_routine.get('id'))
    combined_minutes = (estimated_main_minutes or 0) + (additional_info['total_minutes'] if additional_info else 0)
    
    next_workout_info = {
        'routine_id': next_routine.get('id'),
        'title': next_routine.get('title'),
        'day_number': day_number,
        'folder_id': next_routine.get('folder_id'),
        'estimated_main_minutes': estimated_main_minutes,
        'additional_training': additional_info,
        'combined_training_minutes': combined_minutes,
    }
    
    output_file = os.path.join(output_dir, 'next_workout.json')
    with open(output_file, 'w') as f:
        json.dump(next_workout_info, f, indent=2)


def main():
    """Main function to determine and display next workout."""
    client = HevyAPIClient()
    
    try:
        # Step 1: Get latest qualifying (Day 1-6) workout
        latest_workout = get_most_recent_workout(client)
        if not latest_workout:
            print("No qualifying workouts found (Day 1-6 main muscle groups)")
            return
        
        latest_title = latest_workout.get('title')
        latest_routine_id = latest_workout.get('routine_id')
        current_day = extract_day_number(latest_title)
        if not current_day:
            print(f"Could not extract day number from: {latest_title}")
            return
        
        # Step 2-3: Get routine details to extract folder_id
        current_routine = client.get_routine(latest_routine_id)
        folder_id = current_routine.get('routine', {}).get('folder_id')
        
        if not folder_id:
            print("Could not determine routine folder")
            return
        
        # Step 4-5: Fetch routines in folder and extract day numbers
        folder_routines = get_routines_in_folder(client, folder_id)
        
        # Step 6: Find next routine
        next_routine = get_next_routine(folder_routines, current_day)
        
        if next_routine:
            display_next_workout(client, next_routine)
            save_next_workout_info(client, next_routine)
        else:
            print("Could not find next routine in sequence")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
