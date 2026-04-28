# Exercise Validation Quick Reference

## What Is Exercise Validation?

Exercise validation ensures all exercise IDs in your routine templates match the authoritative source in `exercise_mappings.md`. This prevents upload failures and data integrity issues.

## Quick Start

### See All Valid Exercises

```bash
python exercise_validator.py --list
```

### Validate Your Routine File

```bash
python exercise_validator.py input/my_routine.json
```

### Upload a Routine (Validation Automatic)

```bash
python routine_uploader.py input/my_routine.json

# Session folder override (finds or creates folder for this run)
python routine_uploader.py input/my_routine.json --folder-title "HSF 15"
```

## What Happens During Upload?

1. ✅ **Folder Verification (optional)** - If `--folder-title` is provided, uploader finds or creates that folder for this session
2. ✅ **Validation** - All exercise IDs checked against exercise_mappings.md
3. ✅ **Enhancement** - Warmup weights auto-populated from history
4. ✅ **Upload** - Routine sent to Hevy API

If validation fails, upload stops with helpful error message.

## Fix Invalid Exercise IDs

### You See This Error

```text
❌ Validation failed: 1 exercise(s) not found in exercise_mappings.md
   1. BADID123 - NOT FOUND IN exercise_mappings.md!
```

### Follow These Steps

1. **Find the correct exercise ID**:

   ```bash
   python exercise_validator.py --list | grep -i "exercise_name"
   ```

2. **Copy the correct ID** from the output

3. **Update your routine JSON** with the correct ID

4. **Validate again**:

   ```bash
   python exercise_validator.py input/my_routine.json
   ```

## Advanced: Skip Validation

⚠️ **Only for testing or special cases!**

```bash
python routine_uploader.py input/my_routine.json --no-validate
```

## Useful Commands

| Command | Purpose |
|---------|---------|
| `python exercise_validator.py --list` | Show all available exercises |
| `python exercise_validator.py file.json -v` | Validate with detailed output |
| `python exercise_validator.py --list \| grep -i "biceps"` | Find specific exercise IDs |
| `python routine_uploader.py input/` | Upload all routines in directory |
| `python routine_uploader.py file.json --dry-run` | Preview upload without sending |
| `python routine_uploader.py file.json --dry-run --folder-title "HSF 15"` | Verify session folder + preview upload |

## Categories Available

The validator supports these exercise categories:

- **Biceps** - Biceps curl variations
- **Core** - Ab exercises and planks
- **Espalda** (Back) - Back exercises
- **Hombro** (Shoulders) - Shoulder exercises
- **Pecho** (Chest) - Chest exercises
- **Pierna** (Legs) - Leg exercises
- **Triceps** - Triceps exercises

## Troubleshooting

### I can't find my exercise ID

Run `--list` and search for similar exercises:

```bash
python exercise_validator.py --list | grep -i "your_exercise"
```

If still not found, the exercise may not be in exercise_mappings.md. Add it first.

### Validation says exercise not found but I know it exists

1. Check for typos in the exercise ID
2. Make sure exercise_mappings.md is up to date
3. Compare against the authoritative IDs in `--list` output

### I want to bypass validation

Use `--no-validate` flag (advanced users only):

```bash
python routine_uploader.py input/my_routine.json --no-validate
```

## See Also

- **ROUTINE_ENHANCEMENT.md** - Complete validation documentation
- **VALIDATION_SYSTEM_COMPLETE.md** - Technical implementation details
- **exercise_mappings.md** - Authoritative exercise ID source
