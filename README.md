# 🏋️ Hevy Training Toolkit

> Comprehensive Python toolkit for managing Hevy routines, folders, body measurements, workout history, and progression analysis through a single CLI and API client.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Hevy API](https://img.shields.io/badge/Hevy-API-orange.svg)](https://api.hevyapp.com/docs/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📝 **Routine & Folder Management** | Upload, validate, organize, and batch-process workout routines via Hevy API |
| 🎯 **Workout Retrieval** | Determine the next workout in sequence and update workout notes from recent history |
| 📊 **Progression Tracking** | Track bench press, squat, and shoulder press with 1RM estimation (Epley formula) |
| 📈 **Visualization Suite** | Generate multiple chart styles, dashboards, and comparisons from Hevy data |
| 🔧 **Toolkit CLI & API Client** | Use `hevy_cli.py`, `hevy.sh`, and `HevyAPIClient` as the stable umbrella surface |
| 📏 **Body Measurements** | List, create, fetch, and update Hevy body measurements with safe default update behavior |

---

## 🧭 Project Scope

### Implemented Today

- Routine creation, validation, enhancement, upload, and folder management
- Body measurements retrieval, creation, and update workflows
- Workout retrieval flows for next-workout planning and workout note updates
- Strength progression tracking, visualizations, and exercise history analysis

### Planned Next

- Broader workout-history retrieval and analytics as first-class CLI domains
- Additional Hevy data-management commands under the umbrella toolkit entrypoints

---

## 📸 Visualization Examples

The project generates beautiful, professional-grade charts to track your progress:

### Progression Tracking

- **Standard Progression**: Line charts showing weight and estimated 1RM over time
- **Minimal Style**: Clean, dark-themed visualizations
- **Gradient Style**: Colorful progression using viridis colormap
- **Area Charts**: Stacked visualization of weight and 1RM

### Comprehensive Dashboard

- **6-Panel Dashboard**: All exercises (bench press, squat, shoulder press) with dual metrics
- **Comparison Charts**: Normalized view of all exercises on the same scale

*Sample visualizations are automatically saved to the `visualizations/` directory.*

---

## 📚 Table of Contents

- [Quick Start](#-quick-start)
- [Project Scope](#-project-scope)
- [Progression Tracking](#-progression-tracking--analysis)
- [Routine Management](#-routine-management)
- [CLI Usage](#-cli-usage)
- [API Client Usage](#-api-client-usage)
- [Documentation](#-documentation)
- [Project Structure](#-project-structure)
- [Troubleshooting](#-troubleshooting)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Hevy Pro account (for API access)
- API key from [Hevy Developer Settings](https://hevy.com/settings?developer)

### Installation

```bash
# Clone the repository
git clone <your-repo-url> hevy-training-toolkit
cd hevy-training-toolkit

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add: HEVY_API_KEY=your_key_here
```

If your local checkout still uses the older folder name, keep using that directory name until you rename the repository.

> ⚠️ **Security Note:** See [`SECURITY_SETUP.md`](docs/SECURITY_SETUP.md) for detailed instructions on safely configuring your API key.

### Test Your Setup

```bash
# Verify API connection
python hevy_cli.py auth
```

### 📋 Routine Creation Rules

Before creating routines, read [`ROUTINE_CREATION_RULES.md`](ROUTINE_CREATION_RULES.md) for critical guidelines:

- Rep range interpretation (always use maximum value)
- "Duplicar repeticiones" handling (double reps per set)
- Exercise-specific requirements

---

---

## 📊 Progression Tracking & Analysis

### 🎯 What's Your Next Workout?

Automatically determines your next workout based on your routine sequence:

```bash
python scripts/next_workout.py
```

**How it works** (6-step process):

1. Fetches your most recent completed workout from `/v1/workouts`
2. Extracts the routine ID from that workout
3. Retrieves routine details to get the folder ID
4. Fetches all routines and filters by folder ID (ensures correct routine sequence)
5. Extracts day numbers from routine titles
6. Finds the next routine in numerical sequence (with wraparound)

**Output:**

- Displays all exercises with reps, sets, and notes
- Saves next workout info to `data/next_workout.json` for future reference

**Example:**

```text
Most recent: Day 7 - Back and Shoulders (Day 7)
Folder ID: 1812915
Found 16 routines in folder

YOUR NEXT WORKOUT
📅 Routine: Day 8 - Chest
💪 Total Exercises: 6
Exercises:
  1. Bench Press (Dumbbell) (8 reps) (4 sets)
  2. Incline Bench Press (Dumbbell) (8 reps) (4 sets)
  [...]
```

### 💪 Track Your Strength Progression

Track your gains with automatic 1RM estimation using the Epley formula.

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

### 🎨 Advanced Visualizations

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

### 🔍 Analyze Squat Low-Point Analysis

Identify sessions significantly below your rolling average:

```bash
python scripts/analyze_squat_lowpoints.py
```

Identifies:

- Sessions >5kg below 7-day rolling average
- Chronological low points with context
- Summary statistics and trends

---

## 🖥️ CLI Usage

Use the umbrella CLI for project-level commands:

```bash
# Authenticate against Hevy
python hevy_cli.py auth

# Upload routines
python hevy_cli.py routines upload routine.json --dry-run

# Validate routine JSON
python hevy_cli.py routines validate input/dia_1_pecho_hsf16.json

# Inspect recent folders
python hevy_cli.py folders recent

# List body measurements
python hevy_cli.py measurements list

# Get a measurement entry by date
python hevy_cli.py measurements get 2026-04-26

# Create a measurement entry
python hevy_cli.py measurements create --date 2026-04-26 --weight-kg 80.4 --waist 81

# Update one field while preserving the rest of the entry
python hevy_cli.py measurements update 2026-04-26 --waist 79.5
```

For shell-first workflows, `./hevy.sh` mirrors the same command structure. Existing routine-specific scripts remain available for compatibility.

---

## 📝 Routine Management

### Upload Routines

```bash
# Upload a single routine
python hevy_cli.py routines upload routine.json

# Upload to a specific folder for this session (creates folder if missing)
python hevy_cli.py routines upload routine.json --folder-title "HSF 15"

# Upload all routines from a directory
python hevy_cli.py routines upload ./routines/

# Preview without uploading (dry-run)
python hevy_cli.py routines upload routine.json --dry-run

# Dry-run with session folder verification
python hevy_cli.py routines upload routine.json --dry-run --folder-title "HSF 15"
```

`--folder-title` is session-scoped: it only applies to that command run.
If omitted, uploader uses each routine file's existing `folder_id`.

### View Your Routine Folders

To see all your routine folders and identify the most recent one:

```bash
# Display all folders ranked by recency
python hevy_cli.py folders recent
```

This shows:
- All your routine folders in order (most recent first)
- Folder IDs for API operations
- Highlights the current/most recent folder

### Create a New Routine Folder

When you're ready to upload routines to a new cycle:

```bash
# Auto-increment naming: HSF 15 → HSF 16
# Asks for confirmation before creating
python hevy_cli.py folders create-next
```

Or create with a custom name:

```bash
python hevy_cli.py folders create "Custom Folder Name"
```

For detailed folder management and workflows, see [`docs/ROUTINE_FOLDER_MANAGEMENT.md`](docs/ROUTINE_FOLDER_MANAGEMENT.md).

### Post-Creation Validation Table

After each routine creation, always provide this validation table in chat:

| # | Exercise | Sets x Reps | Intensity | Weight |
|---|---|---|---|---|

This is the standard review format to quickly validate the uploaded routine.

### Update Workout Notes

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

For detailed information, see [`WORKOUT_UPDATE_GUIDE.md`](docs/WORKOUT_UPDATE_GUIDE.md).

---

## 🔧 API Client Usage

### Python API Client Examples

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

### Available Methods

#### Workout Management

- `list_workouts(page=1, page_size=10)` - Get paginated list of workouts (most recent first)
- `get_routine(routine_id)` - Get specific routine with all exercises and sets
- `list_routines(page=1, page_size=10)` - Get paginated list of routines, filterable by folder_id

#### Routine Management

- `create_routine(data)` - Create new routine
- `update_routine(id, data)` - Update routine
- `delete_routine(id)` - Delete routine

#### Exercise & Reference Data

- `get_exercise_history(exercise_template_id)` - Get all sets for a specific exercise
- `get_exercise_templates()` - List available exercises with template IDs
- `create_routine_folder(folder_title)` - Create new folder

#### File Operations

- `create_routine_from_file(path)` - Upload routine from JSON file
- `save_routine_to_file(data, path)` - Save routine to JSON file

---

## 📖 Documentation

### Core Documentation Files

| File | Description |
|------|-------------|
| [`README.md`](README.md) | Complete overview and architecture (this file) |
| [`QUICK_REFERENCE.md`](docs/QUICK_REFERENCE.md) | Quick lookup of commands and exercise IDs |
| [`PROGRESSION_TRACKER_README.md`](docs/PROGRESSION_TRACKER_README.md) | Detailed progression tracking guide |
| [`SECURITY_SETUP.md`](docs/SECURITY_SETUP.md) | Safe API key configuration |
| [`HEVY_API_COMPLETE.md`](docs/HEVY_API_COMPLETE.md) | Complete Hevy API reference |
| [`ROUTINE_CREATION_RULES.md`](ROUTINE_CREATION_RULES.md) | Critical rules for routine creation |

### Quick Commands Reference

```bash
# Test API connection
python hevy_cli.py auth

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
python hevy_cli.py routines upload routine.json

# Upload with per-session folder override
python hevy_cli.py routines upload routine.json --folder-title "HSF 15"
```

---

## 📁 Project Structure

```text
project-root/
├── 📄 hevy_cli.py                  # Umbrella toolkit CLI
├── 📄 hevy.sh                      # Shell wrapper for the umbrella CLI
├── 📄 hevy_api_client.py           # Main API client
├── 📄 routine_uploader.py          # Direct routine upload tool
├── 📄 batch_routine_uploader.py    # Batch routine import tool
├── 📄 test_api_key.py              # API connection test
├── 📄 requirements.txt             # Python dependencies
│
├── 📂 scripts/
│   ├── next_workout.py             # 🎯 What's my next workout?
│   ├── bench_press_progression.py  # Bench press tracking
│   ├── squat_progression.py        # Squat tracking
│   ├── shoulder_press_progression.py # Shoulder press tracking
│   ├── analyze_squat_lowpoints.py  # Low-point detection
│   └── advanced_visualizations.py  # Multi-style charts
│
├── 📂 data/
│   ├── next_workout.json           # Cached next workout
│   ├── bench_press_data_2025.json
│   ├── squat_data_2025.json
│   └── shoulder_press_data_2025.json
│
├── 📂 visualizations/              # Generated PNG charts
│   ├── bench_press_progression_2025.png
│   ├── squat_progression_2025.png
│   ├── *_minimal_2025.png
│   ├── *_gradient_2025.png
│   ├── *_area_2025.png
│   ├── dashboard_2025.png
│   └── comparison_2025.png
│
├── 📂 input/                       # Sample routine JSON files
├── 📂 templates/                   # JSON templates
│   ├── TEMPLATE_routine.json
│   └── EXAMPLE_all_set_types.json
│
└── 📂 docs/                        # Documentation
    ├── NAMING_STRATEGY.md
    ├── QUICK_START.md
    ├── QUICK_REFERENCE.md
    ├── PROGRESSION_TRACKER_README.md
    ├── SECURITY_SETUP.md
    └── ...
```

---

## 🔬 Technical Details

### 1RM Calculation Method

The Epley formula is used across all progression trackers:

```text
1RM = weight × (1 + reps ÷ 30)
```

This provides reasonable estimates for strength progression visualization without requiring actual max attempts.

### Exercise Template IDs

Reference IDs for major exercises:

| Exercise | Template ID |
|----------|-------------|
| Bench Press (Barbell) | `79D0BB3A` |
| Squat (Barbell) | `D04AC939` |
| Shoulder Press (Dumbbell) | `878CD1D0` |
| Lat Pulldown (Cable) | `6A6C31A5` |
| Seated Row (Machine) | `1DF4A847` |
| T Bar Row | `08A2974E` |

Get complete list:

```bash
python -c "from hevy_api_client import HevyAPIClient; client = HevyAPIClient(); import json; print(json.dumps(client.get_exercise_templates(), indent=2))"
```

---

## 🐛 Troubleshooting

### Invalid API Key Error

- Verify API key in `.env` file
- Generate new key from [Hevy Developer Settings](https://hevy.com/settings?developer)
- Make sure account has Hevy Pro access

### Connection Error

- Check internet connectivity
- Verify Hevy API is online at <https://api.hevyapp.com/docs/>

### Common Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| No visualizations generated | Check `visualizations/` directory exists |
| Empty data files | Ensure you have workout history in Hevy |

---

## 📄 License

MIT License - feel free to use this project for your own workout tracking!

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

Made with 💪 for the Hevy community
