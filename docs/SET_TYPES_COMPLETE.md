# Complete Set Types Reference

## Overview
Per official Hevy API documentation (https://api.hevyapp.com/docs/), routines support exactly 4 set types:
- **warmup** - Light preparation sets
- **normal** - Standard working sets
- **dropset** - Weight-reduced progression
- **failure** - Taken to muscular failure

---

## Set Type Reference Table

| Type | Purpose | Common Use | Fields |
|------|---------|-----------|--------|
| `warmup` | Preparation & activation | First set per exercise | weight_kg, reps |
| `normal` | Main working set | 80% of sets | weight_kg, reps |
| `dropset` | Progressive deload | High-intensity finishers | weight_kg, reps |
| `failure` | Intensity tracking | Leg day finishers | weight_kg, reps |

---

## Detailed Examples

### 1. WARMUP - Light Preparation

**When to use:** First set of every exercise
```json
{
  "type": "warmup",
  "weight_kg": 40,
  "reps": 12,
  "notes": "Light prep set before work"
}
```

**Characteristics:**
- Low intensity, high reps (10-15)
- Wakes up the nervous system
- Often auto-populated from exercise history
- Activates muscles for working sets

---

### 2. NORMAL - Standard Working Set

**When to use:** Main strength/hypertrophy work
```json
{
  "type": "normal",
  "weight_kg": 60,
  "reps": 6,
  "notes": "Working set - heavy, low reps"
}
```

**Characteristics:**
- 3-8 reps for strength
- 8-12 reps for hypertrophy
- 12-20 reps for endurance
- Most common set type (80% of training)

**Example progression:**
```
Set 1: 60kg × 6 reps (normal)
Set 2: 60kg × 7 reps (normal)
Set 3: 60kg × 8 reps (normal)
Set 4: 60kg × 8 reps (normal)
```

---

### 3. DROPSET - Weight-Reduced Progression

**When to use:** Final exercise or set of a muscle group
```json
[
  {
    "type": "dropset",
    "weight_kg": 100,
    "reps": 6,
    "notes": "Heavy weight, few reps"
  },
  {
    "type": "dropset",
    "weight_kg": 80,
    "reps": 8,
    "notes": "Reduced weight, more reps"
  },
  {
    "type": "dropset",
    "weight_kg": 60,
    "reps": 10,
    "notes": "Lightest weight, maximum volume"
  }
]
```

**Characteristics:**
- Multiple sub-sets with decreasing weight
- Increases time under tension
- Extends set beyond normal failure
- Usually 10-20 second rest between drops
- Yields 1-2 reps per exercise

**Notation:** `100kg(6) → 80kg(8) → 60kg(10)`

**Use case from your workout:**
```
Deltoides posterior: 2 vueltas x sistema Drop set
= 2 rounds × (6rep + 6rep + 8rep + 10rep; heavy→light, 10-20sec recovery)
```

---

### 4. FAILURE - Muscular Failure

**When to use:** Intensity tracking on leg day
```json
{
  "type": "failure",
  "weight_kg": 30,
  "reps": 10,
  "notes": "Taken to muscular failure - can't do another rep"
}
```

**Characteristics:**
- Explicitly marked as "to failure"
- Tracks maximum effort
- Used for intensity analysis
- Often last set of compound movements

**Example:** `Leg Press - final set, taken to failure`

---

## Real-World Workout Examples

### Día 4 Example - Triceps Drop Sets
```json
{
  "name": "Extensión de los brazos sentado con barra",
  "sets": [
    {"type": "warmup", "weight_kg": 10, "reps": 12},
    {"type": "dropset", "weight_kg": 35, "reps": 6},
    {"type": "dropset", "weight_kg": 30, "reps": 6},
    {"type": "dropset", "weight_kg": 25, "reps": 8},
    {"type": "dropset", "weight_kg": 20, "reps": 10}
  ]
}
```
Note: "2 vuelta x sistema Drop set" = 2 rounds = multiple dropset entries

### Building Your Own Mix

**Chest Day Example:**
```json
{
  "exercise": "Bench Press",
  "sets": [
    {"type": "warmup", "weight_kg": 40, "reps": 12},
    {"type": "normal", "weight_kg": 80, "reps": 5},
    {"type": "normal", "weight_kg": 75, "reps": 7},
    {"type": "normal", "weight_kg": 70, "reps": 8},
    {"type": "failure", "weight_kg": 65, "reps": 10},
    {"type": "amrap", "weight_kg": 50, "reps": 15}
  ]
}
```

---

## Quick Reference for Your Workouts

### From Your Instructions:

**"2 vueltas x sistema Drop set"** = 2 rounds, mark each as `"type": "dropset"`
```
Round 1: 6rep + 6rep + 8rep + 10rep
Round 2: 6rep + 6rep + 8rep + 10rep
```

**"Sentadilla isométrica 3x60seg"** = Isometric hold (use `duration_seconds`)
```json
{"type": "normal", "weight_kg": 0, "reps": 0, "duration_seconds": 60}
```

**"4x6-8rep (85%)"** = 4 normal sets, variable reps
```json
{"type": "normal", "weight_kg": 80, "reps": 6}
{"type": "normal", "weight_kg": 80, "reps": 7}
{"type": "normal", "weight_kg": 80, "reps": 8}
{"type": "normal", "weight_kg": 80, "reps": 8}
```

---

## Validation Rules

✅ **Allowed (per Hevy API documentation):** warmup, normal, dropset, failure
❌ **NOT allowed:** "set", "amrap", "rpe", or any other string

All set types pass through:
- `validate_structure.py` - Checks for valid type
- `./routines.sh check` - Pre-flight validation
- `./routines.sh upload` - Auto-runs structure check

---

## Complete Example

See `EXAMPLE_all_set_types.json` for a working routine using all 6 set types.

Validate it:
```bash
python3 validate_structure.py EXAMPLE_all_set_types.json
```
