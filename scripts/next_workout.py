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
7. Estimate duration from workout history (enabled by default)

Usage:
    python scripts/next_workout.py              # With duration estimation (default)
    python scripts/next_workout.py --no-estimate # Skip duration estimation (faster)
"""

import sys
import os
import json
import re
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hevy_api_client import HevyAPIClient
from typing import Optional, Dict, Any, List, Tuple


def get_most_recent_workout(client: HevyAPIClient) -> Optional[Dict[str, Any]]:
    """Get the most recent completed workout from /v1/workouts."""
    workouts = client.list_workouts(page=1, page_size=1)
    workouts_list = workouts.get('workouts', [])
    
    if not workouts_list:
        return None
    
    return workouts_list[0]


def extract_dia_number(routine_title: str) -> Optional[int]:
    """Extract the día number from a routine title.
    
    Only extracts from main sequence routines (e.g., 'Día 4').
    Ignores core routines with slash pattern (e.g., 'Día 4/10').
    """
    # Match 'Día X' but NOT 'Día X/Y' (core routines)
    match = re.search(r'Día\s*(\d+)(?![/\d])', routine_title, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def is_core_routine(routine_title: str) -> bool:
    """Check if a routine is a core/abs routine.
    
    Detects core routines by:
    1. 'core' keyword in title
    2. 'Día X/Y' pattern (e.g., 'Día 4/10')
    """
    title_lower = routine_title.lower()
    # Check for 'core' keyword
    if 'core' in title_lower:
        return True
    # Check for 'Día X/Y' pattern (indicates core/alternate routine)
    if re.search(r'día\s*\d+/\d+', title_lower):
        return True
    return False


def get_routines_in_folder(client: HevyAPIClient, folder_id: int) -> List[Dict[str, Any]]:
    """Fetch all routines and filter by folder_id, including core routines."""
    all_routines = []
    page = 1
    
    while True:
        response = client.list_routines(page=page, page_size=10)
        routines_page = response.get('routines', [])
        all_routines.extend(routines_page)
        
        if page >= response.get('page_count', 1):
            break
        page += 1
    
    # Filter by folder_id and extract día numbers (including core routines)
    folder_routines = []
    core_routines = []
    
    for routine in all_routines:
        if routine.get('folder_id') == folder_id:
            title = routine.get('title', '')
            
            # Check if it's a core routine
            if is_core_routine(title):
                core_routines.append(routine)
            else:
                dia_number = extract_dia_number(title)
                if dia_number:
                    routine['dia_number'] = dia_number
                    folder_routines.append(routine)
    
    return folder_routines, core_routines


def get_next_routine(folder_routines: List[Dict[str, Any]], core_routines: List[Dict[str, Any]], current_dia: int, last_was_core: bool) -> Optional[Dict[str, Any]]:
    """
    Find next routine by día number, alternating with core routines.
    
    Logic:
    - If last workout was a día routine, check if there's a core routine to do
    - If last workout was core, return next día routine
    - Core routines can be done between any día workouts
    """
    # Sort by día number
    sorted_routines = sorted(folder_routines, key=lambda x: x.get('dia_number', 0))
    
    # If last was core, return next día routine
    if last_was_core:
        # Find routines with día > current_dia
        next_routines = [r for r in sorted_routines if r.get('dia_number', 0) > current_dia]
        
        # If found, return the next one; otherwise wrap around to first
        if next_routines:
            return next_routines[0]
        else:
            return sorted_routines[0] if sorted_routines else None
    
    # Last was a día routine - could suggest core next, or next día
    # For now, return next día (user can manually choose core)
    # Find routines with día > current_dia
    next_routines = [r for r in sorted_routines if r.get('dia_number', 0) > current_dia]
    
    # If found, return the next one; otherwise wrap around to first
    if next_routines:
        return next_routines[0]
    else:
        return sorted_routines[0] if sorted_routines else None


def get_workout_duration_seconds(workout: Dict[str, Any]) -> Optional[int]:
    """Extract duration in seconds from a workout."""
    start = workout.get('start_time')
    end = workout.get('end_time')
    
    if start and end:
        try:
            s = datetime.fromisoformat(start.replace('Z', '+00:00'))
            e = datetime.fromisoformat(end.replace('Z', '+00:00'))
            dur = e - s
            return int(dur.total_seconds())
        except Exception:
            pass
    
    return None


def get_recent_workouts(client: HevyAPIClient, lookback_months: int = 3, max_workouts: int = 30) -> List[Dict[str, Any]]:
    """
    Fetch recent workouts within the lookback period.
    
    Args:
        client: HevyAPIClient instance
        lookback_months: How many months back to fetch (default: 3)
        max_workouts: Maximum number of workouts to fetch (default: 30 for speed)
    
    Returns:
        List of workouts with full details including exercises
    """
    cutoff_date = datetime.now() - timedelta(days=lookback_months * 30)
    recent_workouts = []
    page = 1
    
    while len(recent_workouts) < max_workouts:
        try:
            workouts = client.list_workouts(page=page, page_size=10)
            workouts_list = workouts.get('workouts', [])
            
            if not workouts_list:
                break
            
            for workout in workouts_list:
                # Check date
                workout_date_str = workout.get('start_time') or workout.get('created_at')
                if workout_date_str:
                    try:
                        workout_date = datetime.fromisoformat(workout_date_str.replace('Z', '+00:00'))
                        if workout_date < cutoff_date:
                            # Reached cutoff, stop fetching
                            return recent_workouts
                    except Exception:
                        pass
                
                # Fetch full workout details to get exercises
                workout_id = workout.get('id')
                if workout_id:
                    try:
                        full_workout = client.get_workout(workout_id)
                        recent_workouts.append(full_workout)
                        
                        if len(recent_workouts) >= max_workouts:
                            return recent_workouts
                    except Exception:
                        pass
            
            if page >= workouts.get('page_count', 1):
                break
            
            page += 1
        except Exception:
            break
    
    return recent_workouts


def find_similar_workouts(
    routine_exercises: List[str], 
    workout_logs: List[Dict[str, Any]], 
    min_confidence: float = 0.65
) -> List[Dict[str, Any]]:
    """
    Find similar workouts based on exercise overlap.
    
    Args:
        routine_exercises: List of exercise template IDs from target routine
        workout_logs: Historical workout data
        min_confidence: Minimum similarity threshold (0-1)
    
    Returns:
        List of similar workouts with confidence scores and durations
    """
    similar_workouts = []
    
    for workout in workout_logs:
        # Extract exercise template IDs from workout
        workout_exercises = []
        for exercise in workout.get('exercises', []):
            ex_template_id = exercise.get('exercise_template_id')
            if ex_template_id:
                workout_exercises.append(ex_template_id)
        
        if not workout_exercises:
            continue
        
        # Calculate similarity (what % of routine exercises are in this workout)
        matches = sum(1 for ex in routine_exercises if ex in workout_exercises)
        confidence = matches / len(routine_exercises) if routine_exercises else 0
        
        if confidence >= min_confidence:
            duration = get_workout_duration_seconds(workout)
            if duration:
                similar_workouts.append({
                    'date': workout.get('start_time'),
                    'title': workout.get('title', 'Untitled'),
                    'duration_seconds': duration,
                    'confidence': confidence,
                    'matches': matches,
                    'total_routine_exercises': len(routine_exercises),
                    'workout_exercises': len(workout_exercises)
                })
    
    return sorted(similar_workouts, key=lambda x: x['confidence'], reverse=True)


def get_estimated_duration(client: HevyAPIClient, routine_id: str) -> Optional[Dict[str, Any]]:
    """
    Get estimated workout duration with fallback to similar workouts.
    
    Returns dict with estimation details or None if no estimate available.
    """
    try:
        # Fetch routine details
        routine_response = client.get_routine(routine_id)
        routine_data = routine_response.get('routine', {})
        routine_exercises = [ex.get('exercise_template_id') for ex in routine_data.get('exercises', [])]
        
        if not routine_exercises:
            return None
        
        # Fetch recent workouts (last 3 months)
        recent_workouts = get_recent_workouts(client, lookback_months=3)
        
        if not recent_workouts:
            return None
        
        # Try exact routine match first
        exact_matches = []
        for workout in recent_workouts:
            if workout.get('routine_id') == routine_id:
                duration = get_workout_duration_seconds(workout)
                if duration:
                    exact_matches.append(duration)
        
        if exact_matches:
            avg_seconds = sum(exact_matches) // len(exact_matches)
            return {
                'duration_seconds': avg_seconds,
                'method': 'exact_routine',
                'sample_size': len(exact_matches),
                'confidence': 1.0
            }
        
        # Fallback: Find similar workouts
        similar = find_similar_workouts(routine_exercises, recent_workouts, min_confidence=0.65)
        
        if len(similar) >= 2:
            # Use top 3 most similar workouts
            top_similar = similar[:min(3, len(similar))]
            avg_seconds = sum(w['duration_seconds'] for w in top_similar) // len(top_similar)
            avg_confidence = sum(w['confidence'] for w in top_similar) / len(top_similar)
            
            return {
                'duration_seconds': avg_seconds,
                'method': 'similar_workouts',
                'sample_size': len(top_similar),
                'confidence': avg_confidence,
                'similar_workouts': [
                    {
                        'title': w['title'],
                        'confidence': w['confidence'],
                        'matches': f"{w['matches']}/{w['total_routine_exercises']}"
                    }
                    for w in top_similar
                ]
            }
        
    except Exception as e:
        # Silently fail if estimation not possible
        pass
    
    return None


def format_duration_estimate(estimate: Optional[Dict[str, Any]]) -> str:
    """Format duration estimate for display."""
    if not estimate:
        return "No estimate available"
    
    seconds = estimate['duration_seconds']
    mins = seconds // 60
    
    method = estimate.get('method', 'unknown')
    confidence = estimate.get('confidence', 0)
    sample_size = estimate.get('sample_size', 0)
    
    duration_str = f"~{mins} minutes"
    
    if method == 'exact_routine':
        return f"{duration_str} (based on {sample_size} previous workout{'s' if sample_size > 1 else ''})"
    elif method == 'similar_workouts':
        conf_pct = int(confidence * 100)
        return f"{duration_str} (estimated from {sample_size} similar workout{'s' if sample_size > 1 else ''}, {conf_pct}% match)"
    
    return duration_str


def display_next_workout(client: HevyAPIClient, routine: Dict[str, Any], skip_estimation: bool = False) -> None:
    """Display the next workout details in readable format."""
    routine_id = routine.get('id')
    full_routine = client.get_routine(routine_id)
    routine_data = full_routine.get('routine', {})
    
    print(f"\n📅 Routine: {routine_data.get('title')}")
    print(f"💪 Total Exercises: {len(routine_data.get('exercises', []))}")
    
    # Get estimated duration with enhanced fallback (optional for speed)
    if not skip_estimation:
        try:
            print("⏱️  Calculating estimated duration...", end='', flush=True)
            estimate = get_estimated_duration(client, routine_id)
            print("\r" + " " * 50 + "\r", end='', flush=True)  # Clear the progress line
            
            if estimate:
                print(f"⏱️  {format_duration_estimate(estimate)}")
                
                # Show similar workouts used for estimation if available
                if estimate.get('method') == 'similar_workouts' and estimate.get('similar_workouts'):
                    print(f"\n   Based on similar workouts:")
                    for sw in estimate['similar_workouts'][:3]:  # Limit to 3
                        print(f"     • {sw['title']} ({sw['matches']} exercises match)")
            else:
                print("⏱️  No duration estimate available (not enough historical data)")
        except KeyboardInterrupt:
            print("\r" + " " * 50 + "\r", end='', flush=True)  # Clear the progress line
            print("⏱️  Duration estimation skipped")
        except Exception as e:
            print("\r" + " " * 50 + "\r", end='', flush=True)  # Clear the progress line
            # Silently continue if estimation fails
            pass
    
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


def main():
    """Main function to determine and display next workout."""
    # Check for --estimate flag (default: True, can disable with --no-estimate)
    estimate_duration = '--no-estimate' not in sys.argv
    
    client = HevyAPIClient()
    
    try:
        # Step 1: Get latest workout
        latest_workout = get_most_recent_workout(client)
        if not latest_workout:
            print("No workouts found")
            return
        
        latest_title = latest_workout.get('title')
        latest_routine_id = latest_workout.get('routine_id')
        
        # Check if last workout was a core routine
        last_was_core = is_core_routine(latest_title)
        
        # Extract día number from latest workout (even if not from routine)
        # If it was core, we need to find the last día workout
        if last_was_core:
            print(f"Latest workout: {latest_title} (Core routine)")
            print("Looking for last día workout to determine next...")
            
            # Find the most recent non-core workout
            page = 1
            while page <= 5:
                workouts = client.list_workouts(page=page, page_size=10)
                for workout in workouts.get('workouts', []):
                    workout_title = workout.get('title', '')
                    if not is_core_routine(workout_title):
                        current_dia = extract_dia_number(workout_title)
                        if current_dia:
                            print(f"Last día workout was: {workout_title}")
                            if not latest_routine_id and workout.get('routine_id'):
                                latest_routine_id = workout.get('routine_id')
                            break
                if current_dia:
                    break
                page += 1
        else:
            current_dia = extract_dia_number(latest_title)
        
        # Handle case where workout wasn't created from a routine
        if not latest_routine_id:
            if not last_was_core:
                print(f"Latest workout: {latest_title}")
                print("(Not created from a routine, but using día number to find next)")
            
            # Search through recent workouts to find one with a routine_id (to get folder_id)
            print("Looking for a routine-based workout to determine folder...")
            page = 1
            while page <= 5:  # Check up to 5 pages
                workouts = client.list_workouts(page=page, page_size=10)
                for workout in workouts.get('workouts', []):
                    if workout.get('routine_id'):
                        latest_routine_id = workout.get('routine_id')
                        print(f"Found routine-based workout: {workout.get('title')}")
                        break
                if latest_routine_id:
                    break
                page += 1
            
            if not latest_routine_id:
                print("No routine-based workouts found in recent history")
                return
        
        # Step 2-3: Get routine details to extract folder_id
        current_routine = client.get_routine(latest_routine_id)
        folder_id = current_routine.get('routine', {}).get('folder_id')
        
        if not folder_id:
            print("Could not determine routine folder")
            return
        
        # Step 4-5: Fetch routines in folder and extract día numbers (including core)
        folder_routines, core_routines = get_routines_in_folder(client, folder_id)
        
        # Show core routines available if any
        if core_routines and not last_was_core:
            print(f"\n💡 {len(core_routines)} core routine(s) available in this folder")
        
        # Step 6: Find next routine
        next_routine = get_next_routine(folder_routines, core_routines, current_dia, last_was_core)
        
        if next_routine:
            display_next_workout(client, next_routine, skip_estimation=not estimate_duration)
            save_next_workout_info(next_routine)
        else:
            print("Could not find next routine in sequence")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
