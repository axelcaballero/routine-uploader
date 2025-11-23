# Routine Enhancement - Quick Start Guide

## What's New?

Your routine templates now automatically get warmup weights populated from your workout history! No more manual entry of warmup weights.

## Quick Examples

### Upload routine with auto-enhancement (recommended)

```bash
python routine_uploader.py input/dia_10_biceps_triceps.json
```

### Upload without enhancement

```bash
python routine_uploader.py input/dia_10_biceps_triceps.json --no-enhance
```

### Enhance a routine without uploading

```bash
python routine_enhancer.py input/dia_10_biceps_triceps.json -v
```

### Use average warmup weight instead of most recent

```bash
python routine_uploader.py input/dia_10_biceps_triceps.json --warmup-strategy average
```

## Strategies Explained

- **recent** (default): Uses your most recent warmup weight - best for active exercises
- **average**: Averages your last 5 warmup weights - good for consistency
- **mode**: Uses your most common warmup weight - good for plateaus

## What Gets Enhanced?

Only warmup sets with `weight_kg: 0` get populated. Other fields remain unchanged:

- Normal sets still need weight entered manually
- Reps are not modified (unless you use `-r` flag)

## Example: Before & After

**Before:**

```json
{
  "type": "warmup",
  "weight_kg": 0,
  "reps": 12
}
```

**After (with recent history of 15.0kg warmup):**

```json
{
  "type": "warmup",
  "weight_kg": 15.0,
  "reps": 12
}
```

## Programmatic Usage

```python
from routine_enhancer import RoutineEnhancer

enhancer = RoutineEnhancer()

# Enhance your routine
enhanced = enhancer.enhance_from_file(
    "input/my_routine.json",
    output_path="output/enhanced.json"
)
```

## For More Details

See [ROUTINE_ENHANCEMENT.md](ROUTINE_ENHANCEMENT.md) for complete documentation.

## Test It

Run the test to see it in action:

```bash
python test_enhancement.py
```
