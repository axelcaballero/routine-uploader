#!/usr/bin/env python3
"""
Dumbbell Shoulder Press Progression Tracker
Fetches shoulder press data from Hevy API and visualizes progression over time.
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Tuple
from hevy_api_client import HevyAPIClient

try:
    import matplotlib.pyplot as plt
    import pandas as pd
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


def get_shoulder_press_exercise(client: HevyAPIClient) -> Tuple[str, str]:
    """
    Get the shoulder press exercise template.
    Dumbbell Shoulder Press ID: 878CD1D0
    
    Returns:
        Tuple of (template_id, exercise_name)
    """
    # Using the known Dumbbell Shoulder Press ID from exercise_mappings.md
    template_id = "878CD1D0"
    exercise_name = "Shoulder Press (Dumbbell)"
    
    return template_id, exercise_name


def fetch_shoulder_press_history(client: HevyAPIClient, exercise_template_id: str) -> List[Dict[str, Any]]:
    """
    Fetch shoulder press workout history.
    
    Returns:
        List of workouts with weight and reps
    """
    history = client.get_exercise_history(exercise_template_id)
    
    workouts = []
    for set_data in history.get('exercise_history', []):
        # Extract just the date from the ISO timestamp
        workout_date = set_data.get('workout_start_time', '').split('T')[0]
        
        workouts.append({
            'date': workout_date,
            'weight': set_data.get('weight_kg'),
            'reps': set_data.get('reps'),
            'type': set_data.get('set_type', 'normal'),
            'rpe': set_data.get('rpe'),
            'workout_title': set_data.get('workout_title'),
            'timestamp': set_data.get('workout_start_time')
        })
    
    return sorted(workouts, key=lambda x: x['timestamp'])


def calculate_1rm(weight: float, reps: int) -> float:
    """
    Estimate 1 Rep Max using Epley formula.
    1RM = weight × (1 + reps / 30)
    """
    if reps == 1:
        return weight
    return weight * (1 + reps / 30)


def get_max_by_date(workouts: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Get the maximum weight lifted per session.
    """
    df = pd.DataFrame(workouts)
    df['date'] = pd.to_datetime(df['date'])
    
    # Get max weight per session (group by date)
    max_per_session = df.groupby('date')['weight'].max().reset_index()
    max_per_session.columns = ['date', 'weight']
    max_per_session = max_per_session.sort_values('date')
    
    return max_per_session


def get_estimated_1rm_by_date(workouts: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Get estimated 1RM based on best set per session.
    """
    df = pd.DataFrame(workouts)
    df['date'] = pd.to_datetime(df['date'])
    
    # For each session, calculate 1RM for each set and get the max
    df['estimated_1rm'] = df.apply(lambda row: calculate_1rm(row['weight'], row['reps']), axis=1)
    
    # Get max estimated 1RM per session
    max_1rm = df.groupby('date')['estimated_1rm'].max().reset_index()
    max_1rm = max_1rm.sort_values('date')
    
    return max_1rm


def filter_by_year(workouts: List[Dict[str, Any]], year: int) -> List[Dict[str, Any]]:
    """Filter workouts by year."""
    return [w for w in workouts if datetime.fromisoformat(w['date']).year == year]


def print_summary(workouts: List[Dict[str, Any]], year: int):
    """Print workout summary."""
    print(f"\n=== Dumbbell Shoulder Press Progression - {year} ===")
    print(f"Total sets: {len(workouts)}")
    
    if not workouts:
        print("No workouts found for this year.")
        return
    
    weights = [w['weight'] for w in workouts]
    max_weight = max(weights)
    min_weight = min(weights)
    avg_weight = sum(weights) / len(weights)
    
    print(f"Weight range: {min_weight}kg - {max_weight}kg")
    print(f"Average weight: {avg_weight:.1f}kg")
    
    # Calculate 1RMs
    one_rms = [calculate_1rm(w['weight'], w['reps']) for w in workouts]
    max_1rm = max(one_rms)
    print(f"Estimated max 1RM: {max_1rm:.1f}kg")
    
    print(f"First workout: {workouts[0]['date']}")
    print(f"Latest workout: {workouts[-1]['date']}")


def chart_progression(workouts: List[Dict[str, Any]], year: int, exercise_name: str):
    """Create visualization of shoulder press progression."""
    
    if not MATPLOTLIB_AVAILABLE:
        print("matplotlib not installed. Install with: pip install matplotlib pandas")
        return
    
    # Get data
    max_by_date = get_max_by_date(workouts)
    estimated_1rm = get_estimated_1rm_by_date(workouts)
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    fig.suptitle(f'{exercise_name} Progression - {year}', fontsize=16, fontweight='bold')
    
    # Plot 1: Max weight per session
    ax1 = axes[0]
    ax1.plot(max_by_date['date'], max_by_date['weight'], 
             marker='o', linewidth=2, markersize=6, color='#9b59b6', label='Max weight per session')
    ax1.set_ylabel('Weight (kg)', fontsize=12)
    ax1.set_title('Maximum Weight Lifted Per Session', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Plot 2: Estimated 1RM progression
    ax2 = axes[1]
    ax2.plot(estimated_1rm['date'], estimated_1rm['estimated_1rm'], 
             marker='s', linewidth=2, markersize=6, color='#e67e22', label='Estimated 1RM (Epley)')
    ax2.set_ylabel('1RM Estimate (kg)', fontsize=12)
    ax2.set_xlabel('Date', fontsize=12)
    ax2.set_title('Estimated 1 Rep Max Progression', fontsize=12)
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # Rotate x-axis labels for better readability
    for ax in axes:
        ax.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    
    # Save and show
    filename = f'shoulder_press_progression_{year}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"\n✓ Chart saved to {filename}")
    plt.show()


def main():
    """Main execution."""
    try:
        # Initialize client
        client = HevyAPIClient()
        print("Connected to Hevy API")
        
        # Get shoulder press template
        print("\nSearching for shoulder press exercise...")
        template_id, exercise_name = get_shoulder_press_exercise(client)
        print(f"Found: {exercise_name} (ID: {template_id})")
        
        # Fetch history
        print("\nFetching exercise history...")
        all_workouts = fetch_shoulder_press_history(client, template_id)
        print(f"Found {len(all_workouts)} total sets")
        
        if not all_workouts:
            print("No workout data found.")
            return
        
        # Filter to 2025
        workouts_2025 = filter_by_year(all_workouts, 2025)
        
        if not workouts_2025:
            print("\nNo workouts found for 2025.")
            print("Available years:")
            years = set(datetime.fromisoformat(w['date']).year for w in all_workouts)
            for year in sorted(years):
                count = len([w for w in all_workouts if datetime.fromisoformat(w['date']).year == year])
                print(f"  - {year}: {count} sets")
            return
        
        # Print summary
        print_summary(workouts_2025, 2025)
        
        # Create chart
        print("\nGenerating chart...")
        chart_progression(workouts_2025, 2025, exercise_name)
        
        # Save data to JSON
        data_file = 'shoulder_press_data_2025.json'
        with open(data_file, 'w') as f:
            json.dump(workouts_2025, f, indent=2)
        print(f"✓ Raw data saved to {data_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
