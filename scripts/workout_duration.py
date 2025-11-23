#!/usr/bin/env python3
"""
Get workout duration by flexible keyword matching.
Usage: python scripts/workout_duration.py "keyword"
"""

import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hevy_api_client import HevyAPIClient


def find_workout_by_keyword(keyword: str):
    """Find and display a workout's duration by keyword matching."""
    client = HevyAPIClient()
    
    # Get recent workouts
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
    
    # Search for matching workout
    for workout in all_workouts:
        title = workout.get('title', '')
        if keyword.lower() in title.lower():
            workout_id = workout.get('id')
            full_workout = client.get_workout(workout_id)
            
            title = full_workout.get('title')
            start = full_workout.get('start_time')
            end = full_workout.get('end_time')
            
            print(f"📅 {title}")
            if start and end:
                s = datetime.fromisoformat(start.replace('Z', '+00:00'))
                e = datetime.fromisoformat(end.replace('Z', '+00:00'))
                dur = e - s
                mins = int(dur.total_seconds() // 60)
                secs = int(dur.total_seconds() % 60)
                print(f"⏱️  Duration: {mins}m {secs}s")
            return
    
    print(f"No workout found matching '{keyword}'")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/workout_duration.py <keyword>")
        print("Example: python scripts/workout_duration.py 'pecho'")
        sys.exit(1)
    
    keyword = sys.argv[1]
    find_workout_by_keyword(keyword)
