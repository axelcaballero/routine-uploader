# Exercise Progression Tracker

Organization of visualization scripts, data, and analysis tools for tracking barbell strength progression throughout 2025.

## 📁 Directory Structure

```text
├── scripts/                          # All Python scripts for generating data
│   ├── bench_press_progression.py    # Fetch and chart barbell bench press data
│   ├── squat_progression.py          # Fetch and chart barbell squat data
│   ├── shoulder_press_progression.py # Fetch and chart dumbbell shoulder press data
│   └── analyze_squat_lowpoints.py    # Detailed analysis of squat progression dips
│
├── visualizations/                   # Generated progression charts (PNG images)
│   ├── bench_press_progression_2025.png
│   ├── squat_progression_2025.png
│   └── shoulder_press_progression_2025.png
│
├── data/                             # Raw workout data (JSON format)
│   ├── bench_press_data_2025.json    # 160 bench press sets
│   ├── squat_data_2025.json          # 101 squat sets
│   └── shoulder_press_data_2025.json # 183 shoulder press sets
│
└── analysis/                         # (Reserved for additional analysis scripts)
```

## 🏋️ Exercises Tracked

| Exercise | Type | Sets | Max Weight | 1RM Estimate | Data File |
|----------|------|------|-----------|--------------|-----------|
| Bench Press | Barbell | 160 | 61.2 kg | 81.6 kg | `data/bench_press_data_2025.json` |
| Squat | Barbell | 101 | 70.0 kg | 88.7 kg | `data/squat_data_2025.json` |
| Shoulder Press | Dumbbell | 183 | 40.8 kg | 50.3 kg | `data/shoulder_press_data_2025.json` |

## 🚀 Quick Start

### Generate Fresh Data & Visualizations

Run any of these scripts to fetch the latest data from Hevy API and regenerate charts:

```bash
# Bench press progression
python scripts/bench_press_progression.py

# Squat progression
python scripts/squat_progression.py

# Shoulder press progression
python scripts/shoulder_press_progression.py
```

### Analyze Squat Low Points

Get detailed breakdown of dips in squat performance:

```bash
python scripts/analyze_squat_lowpoints.py
```

Output shows:

- Significant low points (>5kg below 7-day rolling average)
- Chronological workout data sorted by weight
- Summary statistics and overall trends

## 📊 Visualization Details

Each chart includes two graphs:

1. **Top Graph**: Maximum weight lifted per session
2. **Bottom Graph**: Estimated 1-Rep Max (using Epley formula)

Visualization locations:

- `visualizations/bench_press_progression_2025.png`
- `visualizations/squat_progression_2025.png`
- `visualizations/shoulder_press_progression_2025.png`

## 📈 Data Format

All JSON files contain sets with the following structure:

```json
[
  {
    "date": "2025-11-14",
    "weight": 61.2,
    "reps": 8,
    "type": "normal",
    "rpe": 9.5,
    "workout_title": "Día 1 – Pecho y Hombro",
    "timestamp": "2025-11-14T20:01:52+00:00"
  }
]
```

## 🔗 API Integration

All scripts use the `HevyAPIClient` which connects to:

- **Base URL**: `https://api.hevyapp.com`
- **Auth**: API key from environment variable `HEVY_API_KEY`
- **Endpoint**: `/v1/exercise_history/{exerciseTemplateId}`

Exercise template IDs (from `instructions.md`):

- Bench Press (Barbell): `79D0BB3A`
- Squat (Barbell): `D04AC939`
- Shoulder Press (Dumbbell): `878CD1D0`

## 🛠 Dependencies

```text
requests==2.31.0
python-dotenv==1.0.0
matplotlib==3.8.0
pandas==2.1.1
```

Install with: `pip install -r requirements.txt`

## 📝 Creating New Progression Trackers

To add a new exercise, create a script in `scripts/` following this pattern:

```python
from hevy_api_client import HevyAPIClient
import json
from bench_press_progression import (
    fetch_exercise_history,
    calculate_1rm,
    get_max_by_date,
    get_estimated_1rm_by_date,
    chart_progression,
    print_summary,
    filter_by_year
)

# Use the template from existing scripts
# Update: exercise ID, function names, and file names
```

## 📖 Notes

- All data is fetched from Hevy API in real-time when scripts run
- JSON files are regenerated each time a script runs
- Charts are saved at 300 DPI for high quality
- Dates are filtered to 2025 by default (modify `filter_by_year()` to change)

## Last Updated

November 22, 2025
