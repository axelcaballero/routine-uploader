#!/usr/bin/env python3
"""
Detailed Squat Progression Analysis
Identifies and analyzes low points in your squat progression.
"""

import json
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd

# Load the squat data
with open('squat_data_2025.json', 'r') as f:
    workouts = json.load(f)

# Convert to DataFrame for analysis
df = pd.DataFrame(workouts)
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date')

# Get max weight per day
max_per_day = df.groupby('date').agg({
    'weight': 'max',
    'reps': lambda x: df.loc[df['weight'].idxmax(), 'reps'] if len(df) > 0 else 0,
    'workout_title': 'first',
    'rpe': 'first'
}).reset_index()

max_per_day.columns = ['date', 'max_weight', 'reps_at_max', 'workout_title', 'rpe']

print("=" * 80)
print("SQUAT PROGRESSION - 2025 DETAILED ANALYSIS")
print("=" * 80)

# Calculate rolling average
max_per_day['rolling_avg_7day'] = max_per_day['max_weight'].rolling(window=7, min_periods=1).mean()

# Find significant drops (more than 5kg below 7-day rolling average)
max_per_day['deviation'] = max_per_day['max_weight'] - max_per_day['rolling_avg_7day']
low_points = max_per_day[max_per_day['deviation'] < -5].sort_values('deviation')

if len(low_points) > 0:
    print(f"\n📉 Found {len(low_points)} significant low points (>5kg below rolling average):\n")
    
    for idx, row in low_points.iterrows():
        date_str = row['date'].strftime('%Y-%m-%d')
        weight = row['max_weight']
        rolling_avg = row['rolling_avg_7day']
        deviation = row['deviation']
        workout = row['workout_title']
        reps = row['reps_at_max']
        
        print(f"📅 Date: {date_str}")
        print(f"   Workout: {workout}")
        print(f"   Max Weight: {weight:.1f} kg ({reps:.0f} reps)")
        print(f"   7-Day Avg: {rolling_avg:.1f} kg")
        print(f"   Deviation: {deviation:.1f} kg below average")
        
        # Get context - what happened before and after
        current_idx = max_per_day[max_per_day['date'] == row['date']].index[0]
        
        if current_idx > 0:
            prev_day = max_per_day.iloc[current_idx - 1]
            print(f"   Previous day: {prev_day['max_weight']:.1f} kg ({prev_day['date'].strftime('%Y-%m-%d')})")
        
        if current_idx < len(max_per_day) - 1:
            next_day = max_per_day.iloc[current_idx + 1]
            print(f"   Next day: {next_day['max_weight']:.1f} kg ({next_day['date'].strftime('%Y-%m-%d')})")
        
        print()
else:
    print("\n✓ No significant low points found (all sessions within 5kg of 7-day average)")

# Show all sessions sorted by weight
print("\n" + "=" * 80)
print("ALL SESSIONS SORTED BY WEIGHT (LOWEST FIRST):")
print("=" * 80 + "\n")

sorted_sessions = max_per_day.sort_values('max_weight')[['date', 'max_weight', 'reps_at_max', 'workout_title']]

for idx, row in sorted_sessions.head(15).iterrows():
    date_str = row['date'].strftime('%Y-%m-%d')
    weight = row['max_weight']
    reps = row['reps_at_max']
    workout = row['workout_title']
    print(f"{date_str} | {weight:6.1f} kg | {reps:2.0f} reps | {workout}")

# Summary statistics
print("\n" + "=" * 80)
print("SUMMARY STATISTICS:")
print("=" * 80)
print(f"Total session days: {len(max_per_day)}")
print(f"Lowest session: {max_per_day['max_weight'].min():.1f} kg")
print(f"Highest session: {max_per_day['max_weight'].max():.1f} kg")
print(f"Average session: {max_per_day['max_weight'].mean():.1f} kg")
print(f"Median session: {max_per_day['max_weight'].median():.1f} kg")
print(f"Overall trend: {max_per_day['max_weight'].iloc[-1] - max_per_day['max_weight'].iloc[0]:.1f} kg (from first to last)")
