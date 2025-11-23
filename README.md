# Hevy Routine Uploader & Progression Tracker

Comprehensive Python tool for managing and analyzing your Hevy workout routines and tracking your strength progression.

## Features

- ✅ **Progression Tracking**: Track barbell bench press, squat, and dumbbell shoulder press with 1RM estimation
- ✅ **Multiple Visualizations**: 5+ chart styles (minimal, gradient, area, dashboard, comparison)
- ✅ **Next Workout Predictor**: Automatically determines your next workout based on routine sequence
- ✅ **Routine Management**: Upload, list, and manage workout routines via Hevy API
- ✅ **API Client Library**: Full-featured Python client for Hevy API interactions
- ✅ **Data Analysis**: Squat low-point analysis and other analytics

## 📋 ROUTINE CREATION RULES

**IMPORTANT:** Before creating any routines, read [`ROUTINE_CREATION_RULES.md`](ROUTINE_CREATION_RULES.md) which documents critical rules for:
- Rep range interpretation (always use maximum value)
- "Duplicar repeticiones" handling (double reps per set)
- Exercise-specific requirements

Load this file at the start of every chat/session involving routine creation.

## Quick Start

### 1. Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with your API key
cp .env.example .env
# Edit .env and add your HEVY_API_KEY
```

**⚠️ Important Security Note:** See [SECURITY_SETUP.md](SECURITY_SETUP.md) for detailed instructions on safely configuring your API key.

## Progression Tracking & Analysis

### Overview

The progression tracking system monitors your strength development across three major lifts with automatic data fetching from Hevy and multiple visualization styles.

### What's Your Next Workout?

Automatically determines your next workout based on your routine sequence:

```bash
python scripts/next_workout.py
```

**How it works** (6-step process):
1. Fetches your most recent completed workout from `/v1/workouts`
2. Extracts the routine ID from that workout
3. Retrieves routine details to get the folder ID
4. Fetches all routines and filters by folder ID (ensures correct routine sequence)
5. Extracts día numbers from routine titles
6. Finds the next routine in numerical sequence (with wraparound)

**Output:**
- Displays all exercises with reps, sets, and notes
- Saves next workout info to `data/next_workout.json` for future reference

**Example:**
```
Most recent: Día 7 – espalda y hombro (Día 7)
Folder ID: 1812915
Found 16 routines in folder

YOUR NEXT WORKOUT
📅 Routine: Día 8 – Pecho
💪 Total Exercises: 6
Exercises:
  1. Bench Press (Dumbbell) (8 reps) (4 sets)
  2. Incline Bench Press (Dumbbell) (8 reps) (4 sets)
  [...]
```

### Track Progression

Track your strength gains with automatic 1RM estimation using the Epley formula.

#### Barbell Bench Press

```bash
python scripts/bench_press_progression.py
```

- **Data:** 160 sets from 2025
- **Max Weight:** 61.2 kg
- **Estimated 1RM:** 81.6 kg
- **Output:** Visualization with weight vs. 1RM trends + JSON data

#### Barbell Squat

```bash
python scripts/squat_progression.py
```

- **Data:** 101 sets from 2025
- **Max Weight:** 70.0 kg
- **Estimated 1RM:** 88.7 kg
- **Output:** Visualization with low-point markers + JSON data

#### Dumbbell Shoulder Press

```bash
python scripts/shoulder_press_progression.py
```

- **Data:** 183 sets from 2025
- **Max Weight:** 40.8 kg per dumbbell
- **Estimated 1RM:** 50.3 kg
- **Output:** Visualization + JSON data

### Advanced Visualizations

Generate multiple stylized visualization types for all exercises:

```bash
python scripts/advanced_visualizations.py
```

Creates 5 visualization styles:
- **Minimal**: Dark theme, clean lines
- **Gradient**: Colorful progression (viridis colormap)
- **Area**: Weight + 1RM stacked visualization
- **Dashboard**: 6-panel comprehensive view (all 3 lifts × 2 metrics)
- **Comparison**: Normalized all exercises on same scale

Output files saved to `visualizations/` directory.

### Analyze Squat Low-Point Analysis

Identify sessions significantly below your rolling average:

```bash
python scripts/analyze_squat_lowpoints.py
```

Identifies:
- Sessions >5kg below 7-day rolling average
- Chronological low points with context
- Summary statistics and trends

## Workout Management

### Update Workout Notes/Description

Add or update workout description/notes (e.g., location, equipment used):

```python
from hevy_api_client import HevyAPIClient

client = HevyAPIClient()

# Get latest workout and update description
workouts = client.list_workouts(page=1, page_size=1)
latest_id = workouts['workouts'][0]['id']

# Simple one-liner - handles all the complexity internally
result = client.update_workout(latest_id, 'station 24')
print(f"Updated: {result.get('description')}")
```

The `update_workout()` method handles all required fields internally:
- Fetches current workout data
- Cleans exercise data (removes indices, ensures notes are non-empty)
- Sends complete workout payload to API
- Returns the updated workout object

For detailed information, see [WORKOUT_UPDATE_GUIDE.md](WORKOUT_UPDATE_GUIDE.md).

## 2. Upload Routines (Original Feature)

```bash
# Upload a single routine
python routine_uploader.py routine.json

# Upload all routines from a directory
python routine_uploader.py ./routines/

# Preview without uploading (dry-run)
python routine_uploader.py routine.json --dry-run
```


## API Key Setup

1. Get your API key from: [Hevy Developer Settings](https://hevy.com/settings?developer)
2. Create a `.env` file (copy from `.env.example`)
3. Add your key: `HEVY_API_KEY=your_key_here`

## Key Components

### hevy_api_client.py

The core API client with all Hevy API interactions. Key addition:
- `list_routines(page, page_size)` - Now supports pagination to fetch all routines across multiple pages
- `list_workouts(page, page_size)` - Paginated workout list, returns most recent first

### scripts/next_workout.py

**Most important script** - Determines your next workout using the 6-step folder_id-based filtering approach.

Key functions:
- `get_most_recent_workout()` - Fetches latest completed workout
- `get_routines_in_folder()` - Fetches ALL routines and filters by folder_id (ensures correct routine sequence)
- `get_next_routine()` - Finds next routine by día number
- `save_next_workout_info()` - Caches result to `data/next_workout.json`

Why this approach works:
- **Folder ID filtering** prevents mixing routines from different training programs
- **Pagination support** ensures all routines are considered
- **Día number extraction** handles various title formats ("Día 7", "D8", "HSF-2 D8")
- **Saved cache** allows quick lookups without API calls

## Quick Commands Reference

```bash
# Test API connection
python test_api_key.py

# What's my next workout?
python scripts/next_workout.py

# Track barbell bench press progression
python scripts/bench_press_progression.py

# Track barbell squat progression  
python scripts/squat_progression.py

# Track dumbbell shoulder press progression
python scripts/shoulder_press_progression.py

# Analyze squat low points (deloads/plateaus)
python scripts/analyze_squat_lowpoints.py

# Generate all visualization styles
python scripts/advanced_visualizations.py

# Upload a routine
python routine_uploader.py routine.json
```

## Documentation Files

- **README.md** (this file) - Complete overview and architecture
- **QUICK_REFERENCE.md** - Quick lookup of commands and exercise IDs
- **PROGRESSION_TRACKER_README.md** - Detailed progression tracking guide
- **SECURITY_SETUP.md** - Safe API key configuration
- **HEVY_API_COMPLETE.md** - Complete Hevy API reference
- **HEVY_API_SETUP.md** - Initial API setup guide

```json
{
  "routine": {
    "title": "Workout Name",
    "folder_id": null,
    "notes": "Optional notes",
    "exercises": [
      {
        "exercise_template_id": "EXERCISE_ID",
        "superset_id": null,
        "rest_seconds": 60,
        "notes": "Optional",
        "sets": [
          {
            "type": "normal",
            "weight_kg": 100,
            "reps": 10,
            "distance_meters": null,
            "duration_seconds": null,
            "custom_metric": null
          }
        ]
      }
    ]
  }
}
```

## Usage Examples

### Python API Client

```python
from hevy_api_client import HevyAPIClient
import json

# Initialize
client = HevyAPIClient()

# List all routines
routines = client.list_routines()
for r in routines['routines']:
    print(f"- {r['title']}")

# Create routine from dict
with open('routine.json') as f:
    data = json.load(f)
response = client.create_routine(data)
print(f"Created: {response['routine'][0]['id']}")

# Get exercise templates
templates = client.get_exercise_templates()
```

## Available Methods

### HevyAPIClient

**Workout Management:**
- `list_workouts(page=1, page_size=10)` - Get paginated list of workouts (most recent first)
- `get_routine(routine_id)` - Get specific routine with all exercises and sets
- `list_routines(page=1, page_size=10)` - Get paginated list of routines, filterable by folder_id

**Routine Management:**
- `create_routine(data)` - Create new routine
- `update_routine(id, data)` - Update routine
- `delete_routine(id)` - Delete routine

**Exercise & Reference Data:**
- `get_exercise_history(exercise_template_id)` - Get all sets for a specific exercise
- `get_exercise_templates()` - List available exercises with template IDs
- `create_routine_folder(folder_title)` - Create new folder

**File Operations:**
- `create_routine_from_file(path)` - Upload routine from JSON file
- `save_routine_to_file(data, path)` - Save routine to JSON file

## API Architecture

### Next Workout Prediction (6-Step Process)

The `scripts/next_workout.py` demonstrates the complete workflow:

```
Step 1: Get Latest Workout
  └─> /v1/workouts?page=1&page_size=1
      Returns: {workouts: [most_recent_workout]}
      Extract: routine_id, title

Step 2-3: Get Routine Details & Folder
  └─> /v1/routines/{routine_id}
      Returns: {routine: {folder_id, exercises: [...]}}
      Extract: folder_id (tells us which routine family to use)

Step 4-5: Fetch All Routines in Folder
  └─> /v1/routines?page=1&page_size=10 (paginated)
      Loop through all pages
      Filter: routine.folder_id == target_folder_id
      Extract: día number from routine.title

Step 6: Find Next Routine
  └─> Build sorted map of {día_number: routine}
      Return: routine where día_number > current_día
              (or wrap to first if at end)
```

### Key Data Structures

**Routine Response:**
```json
{
  "routine": {
    "id": "uuid",
    "title": "Día 8 – Pecho",
    "folder_id": 1812915,
    "exercises": [
      {
        "title": "Bench Press (Dumbbell)",
        "notes": "4x6-8rep. (85% o más)",
        "sets": [
          {"type": "normal", "weight_kg": 40.8, "reps": 8}
        ]
      }
    ]
  }
}
```

**Workout Response:**
```json
{
  "workouts": [
    {
      "id": "uuid",
      "title": "Día 7 – espalda y hombro",
      "routine_id": "uuid",
      "start_time": "2025-11-21T18:03:18+00:00",
      "exercises": [...]
    }
  ]
}
```

**Exercise History Response:**
```json
{
  "exercise_history": [
    {
      "title": "Bench Press (Barbell)",
      "weight_kg": 61.2,
      "reps": 5,
      "set_type": "normal",
      "rpe": 8
    }
  ]
}
```

### Exercise Template IDs

Reference IDs for major exercises:

```
Bench Press (Barbell):           79D0BB3A
Squat (Barbell):                 D04AC939
Shoulder Press (Dumbbell):       878CD1D0
Lat Pulldown (Cable):            6A6C31A5
Seated Row (Machine):            1DF4A847
T Bar Row:                        08A2974E
```

Get complete list: `python -c "from hevy_api_client import HevyAPIClient; client = HevyAPIClient(); import json; print(json.dumps(client.get_exercise_templates(), indent=2))"`

## Directory Structure

```
routine-uploader/
├── hevy_api_client.py           # Main API client
├── routine_uploader.py          # Routine upload tool
├── test_api_key.py              # API connection test
│
├── scripts/
│   ├── next_workout.py          # 🎯 What's my next workout?
│   ├── bench_press_progression.py
│   ├── squat_progression.py
│   ├── shoulder_press_progression.py
│   ├── analyze_squat_lowpoints.py
│   └── advanced_visualizations.py
│
├── data/
│   ├── next_workout.json        # Cached next workout
│   ├── bench_press_data_2025.json
│   ├── squat_data_2025.json
│   └── shoulder_press_data_2025.json
│
├── visualizations/              # Generated PNG charts
│   ├── bench_press_progression_2025.png
│   ├── squat_progression_2025.png
│   ├── *_minimal_2025.png
│   ├── *_gradient_2025.png
│   ├── *_area_2025.png
│   ├── dashboard_2025.png
│   └── comparison_2025.png
│
├── input/                       # Sample routine JSON files
├── analysis/                    # Analysis outputs
└── docs/
    ├── README.md               # This file
    ├── PROGRESSION_TRACKER_README.md
    ├── QUICK_REFERENCE.md
    └── SECURITY_SETUP.md
```

## 1RM Calculation Method

The Epley formula is used across all progression trackers:

```
1RM = weight × (1 + reps ÷ 30)
```

This provides reasonable estimates for strength progression visualization without requiring actual max attempts.

## API Documentation

Full API docs: https://api.hevyapp.com/docs/

## Troubleshooting

**"Invalid API key" error**
- Verify API key in `.env` file
- Generate new key from https://hevy.com/settings?developer
- Make sure account has Hevy Pro access

**"Connection error"**
- Check internet connectivity
- Verify Hevy API is online

## License

MIT
