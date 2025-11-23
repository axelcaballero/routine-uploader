# Hevy API Integration - Complete Setup

## ✅ Status: WORKING

Your API integration is now fully functional and tested!

## What's Set Up

### 1. **HevyAPIClient** (`src/hevy_api_client.py`)
Complete Python client for interacting with the Hevy API with methods for:
- Creating routines
- Fetching routines and exercise templates
- Updating/deleting routines
- File I/O operations

### 2. **Routine Uploader** (`src/routine_uploader.py`)
Command-line tool to upload routines to Hevy with:
- Single file upload
- Batch upload from directories
- Dry-run preview mode
- Progress feedback

### 3. **Configuration** (`.env`)
Your API credentials are stored securely in `.env`

## Authentication
- **Header**: `api-key`
- **Base URL**: `https://api.hevyapp.com`
- **Endpoints**: `/v1/routines`, `/v1/exercise_templates`, etc.

## Quick Start

### Upload a Single Routine
```bash
python src/routine_uploader.py /path/to/routine.json
```

### Upload All Routines from Directory
```bash
python src/routine_uploader.py data/output/
```

### Preview Before Upload (Dry Run)
```bash
python src/routine_uploader.py routine.json --dry-run
```

## Usage Examples

### In Python Code
```python
from src.hevy_api_client import HevyAPIClient
import json

# Initialize client
client = HevyAPIClient()

# Load and create routine
with open('routine.json', 'r') as f:
    routine_data = json.load(f)

response = client.create_routine(routine_data)
print(f"Created routine: {response['routine'][0]['id']}")
```

### Check Your Routines
```python
client = HevyAPIClient()
routines = client.list_routines()
for routine in routines.get('routines', []):
    print(f"- {routine['title']}")
```

### Get Exercise Templates
```python
templates = client.get_exercise_templates()
for template in templates.get('exercises', []):
    if 'bench' in template['name'].lower():
        print(f"{template['name']}: {template['id']}")
```

## API Methods Available

| Method | Purpose |
|--------|---------|
| `create_routine(data)` | Create new routine |
| `list_routines()` | Get all routines |
| `get_routine(id)` | Get specific routine |
| `update_routine(id, data)` | Update routine |
| `delete_routine(id)` | Delete routine |
| `get_exercise_templates()` | List all exercises |
| `create_routine_from_file(path)` | Upload from file |
| `save_routine_to_file(data, path)` | Save to file |

## Workflow

1. **Process PDFs** to generate routine JSON:
   ```bash
   python src/main.py
   ```

2. **Review** generated routines:
   ```bash
   ls data/output/routines.json
   ```

3. **Test upload** (optional):
   ```bash
   python src/routine_uploader.py data/output/routines.json --dry-run
   ```

4. **Upload to Hevy**:
   ```bash
   python src/routine_uploader.py data/output/routines.json
   ```

## Routine JSON Format

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
            "type": "warmup",
            "weight_kg": 0,
            "reps": 12,
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

## Troubleshooting

### Import Error
Make sure you're in the correct directory:
```bash
cd fitness-routine-processor
```

### API Key Error
Verify `.env` file exists and contains your API key:
```bash
cat .env
```

### Upload Fails
- Check that the JSON format is correct
- Verify exercise_template_id values exist
- Ensure you have internet connectivity

## Testing Results

✅ API authentication working
✅ Can fetch routines (10 found)
✅ Can fetch exercise templates
✅ Successfully uploaded test routine

Sample upload result:
```
Routine: Día 6 – Pierna
Exercises: 6
Status: ✅ Created
ID: e18ab99e-25a1-4a56-82c3-7aa49167e462
```

## Next Steps

You can now:
1. Process your PDF files using `src/main.py`
2. Upload the generated routines to Hevy
3. Automate routine creation and management
4. Integrate with your fitness tracking workflow

Enjoy automated routine management! 💪
