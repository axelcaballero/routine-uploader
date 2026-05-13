# 🏋️ Hevy Routine Uploader Toolkit

> Comprehensive Python toolkit for managing Hevy workout routines and core workout workflows.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Hevy API](https://img.shields.io/badge/Hevy-API-orange.svg)](https://api.hevyapp.com/docs/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎯 **Next Workout Predictor** | Smart algorithm determines your next workout based on routine sequence |
| 📝 **Routine Management** | Upload, list, and manage workout routines via Hevy API |
| 🔧 **API Client Library** | Full-featured Python client for seamless Hevy API interactions |


---

## 📚 Table of Contents

- [Quick Start](#-quick-start)
- [Workout Utilities](#-workout-utilities)
- [Routine Management](#-routine-management)
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
git clone https://github.com/axelcaballero/routine-uploader.git
cd routine-uploader

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add: HEVY_API_KEY=your_key_here
```

> ⚠️ **Security Note:** See [`SECURITY_SETUP.md`](docs/SECURITY_SETUP.md) for detailed instructions on safely configuring your API key.

### Test Your Setup

```bash
# Verify API connection
python test_api_key.py
```

### 📋 Routine Creation Rules

Before creating routines, read [`ROUTINE_CREATION_RULES.md`](ROUTINE_CREATION_RULES.md) for critical guidelines:

- Rep range interpretation (always use maximum value)
- "Duplicar repeticiones" handling (double reps per set)
- Exercise-specific requirements

---

---

## 📊 Workout Utilities

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

---

## 📝 Routine Management

### Upload Routines

```bash
# Upload a single routine
python routine_uploader.py routine.json

# Upload to a specific folder for this session (creates folder if missing)
python routine_uploader.py routine.json --folder-title "HSF 15"

# Upload all routines from a directory
python routine_uploader.py ./routines/

# Preview without uploading (dry-run)
python routine_uploader.py routine.json --dry-run

# Dry-run with session folder verification
python routine_uploader.py routine.json --dry-run --folder-title "HSF 15"
```

`--folder-title` is session-scoped: it only applies to that command run.
If omitted, uploader uses each routine file's existing `folder_id`.

### Print Required Validation Table Format

Use the umbrella CLI to print the exact 4-column table format required in chat:

```bash
python hevy_cli.py routines summary-table input/dia_1_pecho_hsf16.json
```

Output columns are fixed to:

```text
# | source exercise name | Hevy excercise name | Sets x Reps
```

The command also appends a footer line:

```text
Routine note: <routine notes text>
```

`Sets x Reps` includes warmup + working sets (for example `1x12 + 4x8`).

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
| [`QUICK_REFERENCE.md`](docs/QUICK_REFERENCE.md) | Quick lookup of active commands and workflows |
| [`SECURITY_SETUP.md`](docs/SECURITY_SETUP.md) | Safe API key configuration |
| [`HEVY_API_COMPLETE.md`](docs/HEVY_API_COMPLETE.md) | Complete Hevy API reference |
| [`ROUTINE_CREATION_RULES.md`](ROUTINE_CREATION_RULES.md) | Critical rules for routine creation |

### Quick Commands Reference

```bash
# Setup (one-time)
pip install -r requirements.txt
export HEVY_API_KEY=<your-api-key>

# Optional utilities
python test_api_key.py
python scripts/next_workout.py
python routine_uploader.py routine.json
python routine_uploader.py routine.json --folder-title "HSF 15"
```

---

## 📁 Project Structure

```text
routine-uploader/
├── 📄 hevy_api_client.py           # Main API client
├── 📄 routine_uploader.py          # Routine upload tool
├── 📄 test_api_key.py              # API connection test
├── 📄 requirements.txt             # Python dependencies
│
├── 📂 scripts/
│   ├── next_workout.py             # 🎯 What's my next workout?
│   └── workout_duration.py         # Workout duration utility
│
├── 📂 data/
│   ├── next_workout.json           # Cached next workout
│
│
├── 📂 input/                       # Sample routine JSON files
├── 📂 templates/                   # JSON templates
│   ├── TEMPLATE_routine.json
│   └── EXAMPLE_all_set_types.json
│
└── 📂 docs/                        # Documentation
    ├── QUICK_START.md
    ├── QUICK_REFERENCE.md
    └── SECURITY_SETUP.md
```

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
| Empty data files | Ensure you have workout history in Hevy |

---

## 📄 License

MIT License - feel free to use this project for your own workout tracking!

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

Made with 💪 for the Hevy community
