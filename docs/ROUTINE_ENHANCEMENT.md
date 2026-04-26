# Routine Enhancement Feature

## Overview

The routine enhancement feature automatically populates missing warmup weights for new routine templates by looking up historical data from your existing workouts. This eliminates the need to manually enter warmup weights when creating new routines.

## Features

- **Automatic Warmup Weight Population**: When creating a new routine, warmup sets with `weight_kg: 0` are automatically populated with weights from your exercise history
- **Multiple Strategies**: Choose how warmup weights are selected:
  - `recent`: Uses the most recent warmup weight (default)
  - `average`: Averages the last 5 warmup weights for stability
  - `mode`: Uses the most frequently used warmup weight
- **Graceful Degradation**: If no warmup history exists for an exercise, the routine is still uploaded with manual entry needed later
- **Opt-out Option**: Disable auto-enhancement if you prefer manual control
- **Exercise ID Validation**: All exercise IDs are automatically validated against `instructions.md` (the source of truth) to prevent mismatches
- **Validation Enforcement**: Invalid exercise IDs are caught before uploading, with helpful error messages
- **Validation Bypass**: Optional `--no-validate` flag for advanced users who need to skip validation

## Usage

### With the Hevy Toolkit Routine Workflow (Recommended)

When uploading routines, enhancement is enabled by default and validation is automatic:

```bash
# Upload with automatic validation and enhancement (default)
python routine_uploader.py input/dia_10_biceps_triceps.json

# Skip validation if needed (advanced users only)
python routine_uploader.py input/dia_10_biceps_triceps.json --no-validate

# Disable enhancement but keep validation
python routine_uploader.py input/dia_10_biceps_triceps.json --no-enhance

# Use a different strategy
python routine_uploader.py input/dia_10_biceps_triceps.json --warmup-strategy average

# Upload entire directory with enhancement
python routine_uploader.py input/
```

### Exercise Validation

Validate exercise IDs without uploading:

```bash
# Validate a single routine file
python exercise_validator.py input/dia_10_biceps_triceps.json

# Verbose validation with exercise names
python exercise_validator.py input/dia_10_biceps_triceps.json -v

# See all available exercises from instructions.md
python exercise_validator.py --list

# See exercises in a specific category
python exercise_validator.py --list | grep "Triceps"
```

### Standalone Enhancement

You can also enhance routines without uploading:

```bash
# Enhance a single file (modifies in place)
python routine_enhancer.py input/dia_10_biceps_triceps.json -v

# Enhance and save to a new file
python routine_enhancer.py input/dia_10_biceps_triceps.json -o output/enhanced.json -v

# Use average strategy
python routine_enhancer.py input/dia_10_biceps_triceps.json --strategy average

# Set default warmup reps
python routine_enhancer.py input/dia_10_biceps_triceps.json --reps 12
```

### Programmatic Usage

```python
from routine_enhancer import RoutineEnhancer
from hevy_api_client import HevyAPIClient

# Create enhancer
enhancer = RoutineEnhancer()

# Enhance routine data
enhanced = enhancer.enhance_routine(
    routine_data,
    warmup_strategy="recent",
    verbose=True
)

# Or enhance directly from file
enhanced = enhancer.enhance_from_file(
    "input/my_routine.json",
    output_path="output/enhanced_routine.json",
    warmup_strategy="average"
)
```

## How It Works

1. **Exercise History Lookup**: For each exercise in the routine, the system queries your Hevy workout history
2. **Warmup Set Detection**: Identifies all sets marked as "warmup" type from the history
3. **Weight Selection**: Based on the chosen strategy:
   - **Recent**: Takes the most recent warmup weight
   - **Average**: Calculates mean of last 5 warmups (more stable)
   - **Mode**: Finds most common warmup weight (handles plateaus)
4. **Template Update**: Populates `weight_kg` for warmup sets that have value 0

## Exercise ID Validation

To prevent upload errors and ensure consistency, all exercise IDs are automatically validated:

### Validation Process

1. **Source of Truth**: `instructions.md` contains the authoritative mapping of exercise names to template IDs
2. **Automatic Parsing**: The validator uses regex to extract all exercise-to-ID mappings from instructions.md
3. **Routine Checking**: Each exercise ID in your routine is checked against this authoritative source
4. **Early Detection**: Invalid IDs are caught BEFORE upload, preventing failed submissions
5. **User Guidance**: Helpful error messages show which IDs are invalid and how to find valid ones

### Example: Validation Preventing Error

When validating this routine with an invalid ID:

```json
{
  "routine": {
    "title": "Test Invalid Routine",
    "exercises": [
      {
        "exercise_template_id": "INVALIDID",
        "notes": "This ID doesn't exist"
      }
    ]
  }
}
```

The validator catches it immediately:

```text
❌ Validation failed: 1 exercise(s) not found in instructions.md
   1. INVALIDID - NOT FOUND IN instructions.md! Notes: This ID doesn't exist
   Use: python exercise_validator.py --list  to see available exercises
```

### Why This Matters

- **Prevents Wasted Uploads**: No more uploading routines only to have them fail in the Hevy app
- **Data Integrity**: Ensures all routines use correct, verified exercise IDs
- **Source of Truth**: instructions.md remains the single authoritative source for exercise mappings
- **User Confidence**: Know exactly which exercises are supported before uploading

## Example

### Before Enhancement

```json
{
  "routine": {
    "title": "Día 10 – Bíceps y Tríceps",
    "exercises": [
      {
        "exercise_template_id": "37FCC2BB",
        "sets": [
          {
            "type": "warmup",
            "weight_kg": 0,
            "reps": 12
          },
          {
            "type": "normal",
            "weight_kg": 0,
            "reps": 8
          }
        ]
      }
    ]
  }
}
```

### After Enhancement

```json
{
  "routine": {
    "title": "Día 10 – Bíceps y Tríceps",
    "exercises": [
      {
        "exercise_template_id": "37FCC2BB",
        "sets": [
          {
            "type": "warmup",
            "weight_kg": 15.0,
            "reps": 12
          },
          {
            "type": "normal",
            "weight_kg": 0,
            "reps": 8
          }
        ]
      }
    ]
  }
}
```

## API Reference

### RoutineEnhancer

#### `enhance_routine(routine_data, warmup_strategy="recent", warmup_reps=None, verbose=False)`

Enhance a routine template with historical warmup data.

**Parameters:**

- `routine_data` (dict): The routine template to enhance
- `warmup_strategy` (str): "recent", "average", or "mode"
- `warmup_reps` (int, optional): Set warmup reps to this value if they're missing
- `verbose` (bool): Print progress information

**Returns:** Enhanced routine data dictionary

#### `enhance_from_file(input_path, output_path=None, warmup_strategy="recent", warmup_reps=None, verbose=False)`

Enhance a routine from a JSON file and optionally save to a new file.

**Parameters:**

- `input_path` (str): Path to routine template JSON
- `output_path` (str, optional): Where to save enhanced routine (defaults to input_path)
- `warmup_strategy` (str): "recent", "average", or "mode"
- `warmup_reps` (int, optional): Set warmup reps if missing
- `verbose` (bool): Print progress information

**Returns:** Enhanced routine data dictionary

### HevyAPIClient

#### `get_warmup_weight_for_exercise(exercise_template_id, strategy="recent")`

Get a suggested warmup weight for an exercise based on history.

**Parameters:**

- `exercise_template_id` (str): The exercise template ID
- `strategy` (str): "recent", "average", or "mode"

**Returns:** Warmup weight in kg or None if no history

## Command-Line Options

### routine_uploader.py

```bash
--dry-run                  Show what would be done without uploading
--no-enhance              Skip automatic warmup weight population
--no-validate             Skip exercise ID validation (not recommended)
--warmup-strategy STR     Strategy: "recent" (default), "average", or "mode"
```

### exercise_validator.py

```bash
routine_file              Path to routine JSON file to validate (optional)
-i, --instructions FILE   Path to instructions.md (default: instructions.md)
-v, --verbose             Show exercise names and categories for valid IDs
--list                    Show all available exercises from instructions.md
```

### routine_enhancer.py

```bash
-o, --output FILE         Output file path (default: overwrites input)
-s, --strategy STR       Strategy: "recent" (default), "average", or "mode"
-r, --reps INT           Set warmup reps to this value
-v, --verbose            Print detailed progress information
```

## Troubleshooting

### Validation Error: "NOT FOUND IN instructions.md"

This means an exercise ID in your routine doesn't match any ID in `instructions.md`.

**Solution:**

1. Run `python exercise_validator.py --list` to see all valid exercise IDs
2. Find the correct ID for your exercise
3. Update the exercise ID in your routine JSON file
4. Retry upload

Example: If you see this error for Biceps Curl:

```text
⚠ 1. BADID123 - NOT FOUND IN instructions.md! Notes: Biceps Curl
```

Run `--list` to find the correct ID:

```bash
python exercise_validator.py --list | grep -i "curl"
```

Then update your JSON with the correct ID from the output.

### "No warmup history found" for an exercise

This means that exercise hasn't been used in any previous workouts. You'll need to manually enter the warmup weight, or the system will use 0kg.

### Enhancement fails silently

If enhancement encounters an error, the original routine is still uploaded unchanged. Check your API key is valid and that you're connected to the internet.

### Warmup weight seems too low/high

Try using `--warmup-strategy average` for a more stable weight (averages last 5 warmups), or manually override with a specific weight in the template.

### Bypassing Validation for Advanced Users

If you need to skip validation (not recommended), use `--no-validate`:

```bash
python routine_uploader.py input/my_routine.json --no-validate
```

**Warning**: This should only be used if:

- You're testing with placeholder data
- You're manually verifying IDs are correct
- You have a very specific reason not to validate

Always validate before real uploads!

## Best Practices

1. **Use Recent Strategy**: For active exercises, "recent" strategy is usually best as it reflects your current strength level

2. **Use Average for Consistency**: If your warmup weight varies, "average" provides more stable starting points

3. **Pre-test with Dry-run**: Use `--dry-run` flag to preview enhanced routine before uploading

4. **Manual Override**: You can still manually edit the routine JSON if you want specific warmup weights

5. **Batch Enhancement**: Enhance multiple routines at once by pointing to a directory:

```bash
python routine_enhancer.py input/ -o output/ -v
```

## Development

To test the enhancement system:

```bash
python test_enhancement.py
```

This runs a mock test that demonstrates the enhancement without needing actual API calls.
