# Workout Update Guide

## Overview

This guide documents how to update workout information (such as description/notes) via the Hevy API.

## API Endpoint

**PUT** `/v1/workouts/{workoutId}`

Updates a specific workout with new information.

## Required Fields

When updating a workout, the API requires the following fields in the request:

- `title` - Workout title (string)
- `description` - Workout notes/description (string)
- `start_time` - Workout start timestamp (ISO 8601 format)
- `end_time` - Workout end timestamp (ISO 8601 format)
- `is_private` - Whether workout is private (boolean)
- `exercises` - Array of exercise objects with sets

## Request Format

```json
{
  "workout": {
    "title": "Día 8 – Pecho",
    "description": "station 24",
    "start_time": "2025-11-22T19:38:40+00:00",
    "end_time": "2025-11-22T20:44:12+00:00",
    "is_private": false,
    "exercises": [
      {
        "exercise_template_id": "3601968B",
        "notes": "4x6-8rep. (85% o más)",
        "sets": [
          {
            "type": "warmup",
            "weight_kg": 18.14,
            "reps": 12,
            "rpe": 6,
            "distance_meters": null,
            "duration_seconds": null,
            "custom_metric": null
          },
          {
            "type": "normal",
            "weight_kg": 45.36,
            "reps": 8,
            "rpe": 9.5,
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

## Important Notes

### Allowed Fields in Sets
Each set in the exercises array can include:
- `type` - "warmup", "normal", or "dropset"
- `weight_kg` - Weight in kilograms
- `reps` - Number of repetitions
- `rpe` - Rate of Perceived Exertion (0-10 scale)
- `distance_meters` - Distance for cardio exercises
- `duration_seconds` - Duration for timed sets
- `custom_metric` - Custom metric value

### Not Allowed
- `index` - Cannot include field indices
- Empty `notes` - Exercise notes must have at least one character (use "-" as placeholder)

### Exercise Notes
- If `notes` is empty string, use "-" as a placeholder
- This is required by the API validation

## Python Implementation

### Using HevyAPIClient

```python
from hevy_api_client import HevyAPIClient

client = HevyAPIClient()

# Get latest workout
workouts = client.list_workouts(page=1, page_size=1)
latest = workouts['workouts'][0]
workout_id = latest.get('id')

# Prepare clean exercise data
exercises = []
for ex in latest.get('exercises', []):
    clean_ex = {
        'exercise_template_id': ex.get('exercise_template_id'),
        'notes': ex.get('notes') or '-',  # Ensure notes is not empty
        'sets': []
    }
    
    for s in ex.get('sets', []):
        clean_set = {
            'type': s.get('type'),
            'weight_kg': s.get('weight_kg'),
            'reps': s.get('reps'),
            'distance_meters': s.get('distance_meters'),
            'duration_seconds': s.get('duration_seconds'),
            'custom_metric': s.get('custom_metric'),
            'rpe': s.get('rpe')
        }
        clean_ex['sets'].append(clean_set)
    
    exercises.append(clean_ex)

# Prepare update data
data = {
    'workout': {
        'title': latest.get('title'),
        'description': 'station 24',  # New description
        'start_time': latest.get('start_time'),
        'end_time': latest.get('end_time'),
        'exercises': exercises,
        'is_private': latest.get('is_private', False)
    }
}

# Update the workout
result = client._make_request('PUT', f'/v1/workouts/{workout_id}', data=data)
print(f"Updated description: {result.get('description')}")
```

## Common Workflow

### 1. Get Latest Workout
```python
workouts = client.list_workouts(page=1, page_size=1)
latest = workouts['workouts'][0]
```

### 2. Extract Required Fields
```python
workout_id = latest.get('id')
title = latest.get('title')
description = latest.get('description')
start_time = latest.get('start_time')
end_time = latest.get('end_time')
is_private = latest.get('is_private', False)
exercises = latest.get('exercises', [])
```

### 3. Clean Exercise Data
- Ensure all exercise `notes` fields are non-empty (use "-" if blank)
- Remove `index` fields from exercises and sets
- Keep all essential set data: type, weight_kg, reps, rpe, etc.

### 4. Prepare Update Payload
Wrap cleaned data in `{ "workout": { ... } }` structure

### 5. Send PUT Request
```python
client._make_request('PUT', f'/v1/workouts/{workout_id}', data=data)
```

### 6. Verify Update
```python
workouts = client.list_workouts(page=1, page_size=1)
updated = workouts['workouts'][0]
print(f"New description: {updated.get('description')}")
```

## Example: Add "station 24" to Latest Workout

```python
from hevy_api_client import HevyAPIClient

client = HevyAPIClient()

# Get latest workout
workouts = client.list_workouts(page=1, page_size=1)
latest = workouts['workouts'][0]
workout_id = latest.get('id')

# Clean exercises
exercises = []
for ex in latest.get('exercises', []):
    clean_ex = {
        'exercise_template_id': ex.get('exercise_template_id'),
        'notes': ex.get('notes') or '-',
        'sets': [
            {
                'type': s.get('type'),
                'weight_kg': s.get('weight_kg'),
                'reps': s.get('reps'),
                'distance_meters': s.get('distance_meters'),
                'duration_seconds': s.get('duration_seconds'),
                'custom_metric': s.get('custom_metric'),
                'rpe': s.get('rpe')
            }
            for s in ex.get('sets', [])
        ]
    }
    exercises.append(clean_ex)

# Update
data = {
    'workout': {
        'title': latest.get('title'),
        'description': 'station 24',
        'start_time': latest.get('start_time'),
        'end_time': latest.get('end_time'),
        'exercises': exercises,
        'is_private': latest.get('is_private', False)
    }
}

result = client._make_request('PUT', f'/v1/workouts/{workout_id}', data=data)
print(f"✅ Updated: {result.get('description')}")
```

## Troubleshooting

### Error: "workout" is required
- Ensure data is wrapped in `{ "workout": { ... } }`

### Error: "workout.title" is required
- Include the `title` field in the workout object

### Error: "workout.exercises[0].notes" is not allowed to be empty
- Set empty notes to "-" or another placeholder string

### Error: "workout.exercises[0].sets[0].index" is not allowed
- Remove `index` fields from exercises and sets before sending

### Error: "workout.is_private" is required
- Include the `is_private` boolean field

## Best Practices

1. **Always fetch the latest workout data** before updating to ensure you have all required fields
2. **Clean exercise data** by removing indices and ensuring notes are non-empty
3. **Verify the update** by fetching the workout again to confirm changes were applied
4. **Preserve all set data** even if only updating the description - include all fields
5. **Use the HevyAPIClient** wrapper for consistent error handling

## API Response

On successful update (HTTP 200), the API returns the updated workout object with all fields.

## Data Types Reference

| Field | Type | Example | Required |
|-------|------|---------|----------|
| title | string | "Día 8 – Pecho" | Yes |
| description | string | "station 24" | Yes |
| start_time | ISO 8601 | "2025-11-22T19:38:40+00:00" | Yes |
| end_time | ISO 8601 | "2025-11-22T20:44:12+00:00" | Yes |
| is_private | boolean | false | Yes |
| exercises | array | [...] | Yes |
| exercise.exercise_template_id | string | "3601968B" | Yes |
| exercise.notes | string | "4x6-8rep." | Yes (non-empty) |
| set.type | enum | "normal" | Yes |
| set.weight_kg | number | 45.36 | No |
| set.reps | number | 8 | No |
| set.rpe | number | 9.5 | No |
