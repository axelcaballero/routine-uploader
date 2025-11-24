#!/usr/bin/env python3
"""
Advanced Visualization Generator
Creates stylized charts for exercise progression with various themes.
"""

import json
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Rectangle
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


def load_data(data_file: str) -> List[Dict[str, Any]]:
    """Load workout data from JSON file."""
    with open(f'data/{data_file}', 'r') as f:
        return json.load(f)


def prepare_dataframe(workouts: List[Dict[str, Any]]) -> pd.DataFrame:
    """Convert workout list to DataFrame with max per session."""
    df = pd.DataFrame(workouts)
    df['date'] = pd.to_datetime(df['date'])
    
    # Get max weight per day
    max_per_day = df.groupby('date').agg({
        'weight': 'max',
        'reps': lambda x: df.loc[df['weight'].idxmax(), 'reps'] if len(df) > 0 else 0,
    }).reset_index()
    
    return max_per_day.sort_values('date')


def calculate_1rm(weight: float, reps: int) -> float:
    """Estimate 1RM using Epley formula."""
    if reps == 1:
        return weight
    return weight * (1 + reps / 30)


def style_dark_theme():
    """Apply dark theme styling."""
    plt.style.use('dark_background')
    return {
        'primary': '#00D9FF',
        'secondary': '#FF006E',
        'accent': '#FFBE0B',
        'grid': '#333333'
    }


def create_minimal_chart(exercise_name: str, data_file: str, year: int):
    """Create a minimal, clean visualization."""
    workouts = load_data(data_file)
    df = prepare_dataframe(workouts)
    df['1rm'] = df.apply(lambda row: calculate_1rm(row['weight'], row['reps']), axis=1)
    
    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor('#0f0f0f')
    ax.set_facecolor('#0f0f0f')
    
    # Main line
    ax.plot(df['date'], df['weight'], linewidth=3, color='#00D9FF', label='Weight', zorder=3)
    ax.fill_between(df['date'], df['weight'], alpha=0.15, color='#00D9FF')
    
    ax.set_xlabel('Date', fontsize=12, color='#999999')
    ax.set_ylabel('Weight (kg)', fontsize=12, color='#999999')
    ax.set_title(f'{exercise_name} - {year}', fontsize=18, color='white', pad=20, weight='bold')
    
    ax.grid(True, alpha=0.1, color='#333333', linestyle='-', linewidth=0.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#333333')
    ax.spines['bottom'].set_color('#333333')
    
    ax.tick_params(colors='#999999')
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    filename = f'visualizations/{exercise_name.lower().replace(" ", "_")}_minimal_{year}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='#0f0f0f')
    print(f"✓ Minimal chart saved: {filename}")
    plt.close()


def create_gradient_chart(exercise_name: str, data_file: str, year: int):
    """Create a chart with gradient fill visualization."""
    workouts = load_data(data_file)
    df = prepare_dataframe(workouts)
    df['1rm'] = df.apply(lambda row: calculate_1rm(row['weight'], row['reps']), axis=1)
    
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#f8f9fa')
    
    # Create gradient effect with multiple filled areas
    colors = ['#FF6B6B', '#FFA500', '#FFD93D', '#6BCB77', '#4D96FF']
    n_sections = len(colors)
    
    # Plot line
    ax.plot(df['date'], df['weight'], linewidth=4, color='#2D3436', label='Max Weight', zorder=5)
    
    # Add scatter points
    scatter = ax.scatter(df['date'], df['weight'], c=range(len(df)), cmap='viridis', 
                        s=100, alpha=0.7, edgecolors='white', linewidth=2, zorder=4)
    
    ax.set_xlabel('Date', fontsize=13, weight='bold')
    ax.set_ylabel('Weight (kg)', fontsize=13, weight='bold')
    ax.set_title(f'{exercise_name} Progression - {year}', fontsize=18, weight='bold', pad=20)
    
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_facecolor('#f8f9fa')
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Progression →', rotation=270, labelpad=20, weight='bold')
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    filename = f'visualizations/{exercise_name.lower().replace(" ", "_")}_gradient_{year}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Gradient chart saved: {filename}")
    plt.close()


def create_area_chart(exercise_name: str, data_file: str, year: int):
    """Create a stacked area chart with 1RM estimation."""
    workouts = load_data(data_file)
    df = prepare_dataframe(workouts)
    df['1rm'] = df.apply(lambda row: calculate_1rm(row['weight'], row['reps']), axis=1)
    df['estimated_volume'] = df['weight'] * 5  # Estimated training volume
    
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor('#1a1a1a')
    ax.set_facecolor('#1a1a1a')
    
    # Area chart
    ax.fill_between(df['date'], 0, df['weight'], label='Max Weight', 
                    alpha=0.4, color='#FF6B9D', linewidth=2)
    ax.fill_between(df['date'], df['weight'], df['1rm'], label='1RM Estimate', 
                    alpha=0.3, color='#FFA502', linewidth=2)
    
    ax.plot(df['date'], df['weight'], color='#FF6B9D', linewidth=3, marker='o', markersize=6)
    ax.plot(df['date'], df['1rm'], color='#FFA502', linewidth=3, marker='s', markersize=6)
    
    ax.set_xlabel('Date', fontsize=12, color='white', weight='bold')
    ax.set_ylabel('Weight (kg)', fontsize=12, color='white', weight='bold')
    ax.set_title(f'{exercise_name} - Weight & 1RM Progression - {year}', 
                fontsize=16, color='white', pad=20, weight='bold')
    
    ax.grid(True, alpha=0.2, color='#333333')
    ax.legend(loc='upper left', fontsize=11, framealpha=0.9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#333333')
    ax.spines['bottom'].set_color('#333333')
    
    ax.tick_params(colors='#cccccc')
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    filename = f'visualizations/{exercise_name.lower().replace(" ", "_")}_area_{year}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='#1a1a1a')
    print(f"✓ Area chart saved: {filename}")
    plt.close()


def create_dashboard(year: int = 2025):
    """Create a comprehensive dashboard with all exercises."""
    files = [
        ('bench_press_data_2025.json', 'Bench Press'),
        ('squat_data_2025.json', 'Squat'),
        ('shoulder_press_data_2025.json', 'Shoulder Press')
    ]
    
    fig = plt.figure(figsize=(18, 12))
    fig.patch.set_facecolor('#0a0e27')
    fig.suptitle(f'2025 Strength Progression Dashboard', fontsize=22, color='white', 
                weight='bold', y=0.98)
    
    for idx, (data_file, name) in enumerate(files, 1):
        workouts = load_data(data_file)
        df = prepare_dataframe(workouts)
        df['1rm'] = df.apply(lambda row: calculate_1rm(row['weight'], row['reps']), axis=1)
        
        ax = plt.subplot(2, 3, idx)
        ax.set_facecolor('#0f1535')
        
        # Weight progression
        ax.plot(df['date'], df['weight'], color='#00D9FF', linewidth=2.5, label='Weight', marker='o', markersize=4)
        ax.fill_between(df['date'], df['weight'], alpha=0.2, color='#00D9FF')
        
        ax.set_title(name, fontsize=14, color='#00D9FF', weight='bold', pad=10)
        ax.grid(True, alpha=0.15, color='#1a2a4a')
        ax.tick_params(colors='#888888', labelsize=9)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#1a2a4a')
        ax.spines['bottom'].set_color('#1a2a4a')
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=8)
        
        # 1RM progression
        ax2 = plt.subplot(2, 3, idx + 3)
        ax2.set_facecolor('#0f1535')
        
        ax2.plot(df['date'], df['1rm'], color='#FF006E', linewidth=2.5, label='1RM Est.', marker='s', markersize=4)
        ax2.fill_between(df['date'], df['1rm'], alpha=0.2, color='#FF006E')
        
        ax2.set_title(f'{name} (1RM)', fontsize=14, color='#FF006E', weight='bold', pad=10)
        ax2.grid(True, alpha=0.15, color='#1a2a4a')
        ax2.tick_params(colors='#888888', labelsize=9)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['left'].set_color('#1a2a4a')
        ax2.spines['bottom'].set_color('#1a2a4a')
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=8)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    filename = f'visualizations/dashboard_{year}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='#0a0e27')
    print(f"✓ Dashboard saved: {filename}")
    plt.close()


def create_comparison_chart(year: int = 2025):
    """Create a side-by-side comparison of all three exercises."""
    files = [
        ('bench_press_data_2025.json', 'Bench Press', '#FF6B6B'),
        ('squat_data_2025.json', 'Squat', '#4ECDC4'),
        ('shoulder_press_data_2025.json', 'Shoulder Press', '#FFE66D')
    ]
    
    fig, ax = plt.subplots(figsize=(15, 8))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#f5f5f5')
    
    for data_file, name, color in files:
        workouts = load_data(data_file)
        df = prepare_dataframe(workouts)
        
        # Normalize to starting point for comparison
        normalized = (df['weight'] - df['weight'].iloc[0]) / df['weight'].iloc[0] * 100
        
        ax.plot(df['date'], normalized, label=name, linewidth=3, color=color, marker='o', markersize=6)
    
    ax.axhline(y=0, color='black', linestyle='--', alpha=0.3, linewidth=1)
    ax.set_xlabel('Date', fontsize=12, weight='bold')
    ax.set_ylabel('Progression (%)', fontsize=12, weight='bold')
    ax.set_title('Strength Progression Comparison - 2025 (Normalized)', fontsize=16, weight='bold', pad=20)
    
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=12, loc='best', framealpha=0.9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    filename = f'visualizations/comparison_{year}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Comparison chart saved: {filename}")
    plt.close()


def main():
    """Generate all stylized visualizations."""
    if not MATPLOTLIB_AVAILABLE:
        print("matplotlib not installed. Install with: pip install matplotlib pandas")
        return
    
    print("Generating stylized visualizations...\n")
    
    exercises = [
        ('bench_press_data_2025.json', 'Bench Press'),
        ('squat_data_2025.json', 'Squat'),
        ('shoulder_press_data_2025.json', 'Shoulder Press')
    ]
    
    print("📊 Creating minimal charts...")
    for data_file, name in exercises:
        create_minimal_chart(name, data_file, 2025)
    
    print("\n🎨 Creating gradient charts...")
    for data_file, name in exercises:
        create_gradient_chart(name, data_file, 2025)
    
    print("\n📈 Creating area charts...")
    for data_file, name in exercises:
        create_area_chart(name, data_file, 2025)
    
    print("\n📊 Creating dashboard...")
    create_dashboard(2025)
    
    print("\n🔄 Creating comparison chart...")
    create_comparison_chart(2025)
    
    print("\n✅ All visualizations generated successfully!")
    print("\nGenerated files:")
    print("  - *_minimal_2025.png (clean, minimalist style)")
    print("  - *_gradient_2025.png (colorful with progression gradient)")
    print("  - *_area_2025.png (area charts with weight and 1RM)")
    print("  - dashboard_2025.png (comprehensive 6-panel dashboard)")
    print("  - comparison_2025.png (all exercises normalized comparison)")


if __name__ == "__main__":
    main()
