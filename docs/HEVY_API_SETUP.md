# Hevy API Integration Guide

## Setup

### 1. Get Your API Key
1. Go to [https://app.hevy.io/settings/api](https://app.hevy.io/settings/api)
2. Generate a new API key
3. Copy the key

### 2. Configure Environment
Create a `.env` file in the `fitness-routine-processor` directory:

```bash
cp .env.example .env
```

Then edit `.env` and add your API key:

```
HEVY_API_KEY=your_api_key_here
```

**Important**: Never commit `.env` to version control!

### 3. Verify Dependencies
Dependencies are already installed:
- `requests` - for HTTP calls
- `python-dotenv` - for environment variables

## Usage

### Option 1: Upload Individual Routine Files

Upload a routine from a JSON file:

```bash
python src/routine_uploader.py /path/to/routine.json
```

### Option 2: Upload Multiple Routines

Upload all routines from a directory:

```bash
python src/routine_uploader.py data/output/
```

### Option 3: Dry Run (Preview)

See what would be uploaded without actually uploading:

```bash
python src/routine_uploader.py routine.json --dry-run
```

### Option 4: Use the API Client Directly

In Python code:

```python
from src.hevy_api_client import HevyAPIClient
import json

# Initialize client
client = HevyAPIClient()

# Load routine from file
with open('routine.json', 'r') as f:
    routine_data = json.load(f)

# Create routine
response = client.create_routine(routine_data)
print(f"Created routine with ID: {response['id']}")
```

## API Client Methods

### Creating Routines
```python
# Create from dict
routine_response = client.create_routine(routine_data)

# Create from file
routine_response = client.create_routine_from_file('routine.json')
```

### Reading Routines
```python
# List all routines
all_routines = client.list_routines()

# Get specific routine
routine = client.get_routine('routine_id')
```

### Updating/Deleting
```python
# Update routine
updated = client.update_routine('routine_id', updated_data)

# Delete routine
client.delete_routine('routine_id')
```

### Other Operations
```python
# Get available exercises
templates = client.get_exercise_templates()

# Save routine to file
client.save_routine_to_file(routine_data, 'output.json')
```

## Routine JSON Format

Required structure:

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
        "notes": "Optional exercise notes",
        "sets": [
          {
            "type": "warmup",
            "weight_kg": 0,
            "reps": 12,
            "distance_meters": null,
            "duration_seconds": null,
            "custom_metric": null
          },
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

## Finding Exercise Template IDs

To find the correct exercise template IDs for your exercises:

```python
from src.hevy_api_client import HevyAPIClient

client = HevyAPIClient()
templates = client.get_exercise_templates()

# Search for specific exercise
for exercise in templates['exercises']:
    if 'bench' in exercise['name'].lower():
        print(f"{exercise['name']}: {exercise['id']}")
```

## Troubleshooting

### "API key not provided" Error
- Make sure you've created a `.env` file
- Verify the file contains `HEVY_API_KEY=your_key`
- Check that you copied the full API key correctly

### 401 Unauthorized
- Your API key may be invalid or expired
- Generate a new key from the Hevy settings
- Update your `.env` file

### Connection Errors
- Verify you have internet connectivity
- The Hevy API may be temporarily unavailable
- Check the Hevy status page

### JSON Format Errors
- Ensure exercise_template_id values are valid
- Verify the JSON structure matches the format above
- Use a JSON validator to check for syntax errors

## Workflow Example

```bash
# 1. Process PDF files to generate routine JSON
python src/main.py

# 2. Review the generated routine in data/output/
ls data/output/routines.json

# 3. Test with dry-run first
python src/routine_uploader.py data/output/routines.json --dry-run

# 4. Upload to Hevy
python src/routine_uploader.py data/output/routines.json
```

## API Rate Limits

The Hevy API may have rate limits. If you encounter rate limit errors:
- Wait a few seconds before retrying
- Consider batching multiple requests
- Contact Hevy support if limits are too restrictive

## Support

- Hevy API Documentation: [https://api.hevy.io/docs](https://api.hevy.io/docs)
- Hevy Support: [https://hevy.io/support](https://hevy.io/support)
