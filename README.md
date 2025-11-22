# Hevy Routine Uploader

Python tool to create and upload workout routines to the Hevy API.

## Features

- ✅ Upload workout routines to Hevy via API
- ✅ Batch upload multiple routines
- ✅ Dry-run mode to preview before uploading
- ✅ Full Hevy API client library

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

### 2. Upload Routines

```bash
# Upload a single routine
python routine_uploader.py routine.json

# Upload all routines from a directory
python routine_uploader.py ./routines/

# Preview without uploading (dry-run)
python routine_uploader.py routine.json --dry-run
```

## API Key Setup

1. Get your API key from: https://hevy.com/settings?developer
2. Create a `.env` file (copy from `.env.example`)
3. Add your key: `HEVY_API_KEY=your_key_here`

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

- `create_routine(data)` - Create new routine
- `list_routines()` - Get all routines
- `get_routine(id)` - Get specific routine
- `update_routine(id, data)` - Update routine
- `delete_routine(id)` - Delete routine
- `get_exercise_templates()` - List available exercises
- `create_routine_from_file(path)` - Upload from file
- `save_routine_to_file(data, path)` - Save to file

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
