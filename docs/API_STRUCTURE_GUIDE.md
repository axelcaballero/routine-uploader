# Hevy API Routine Structure Guide

## Critical Issues Encountered

### 1. ❌ Incorrect JSON Structure (Root Cause of First Failure)
**Error:** `API Error: 400 - {"error":"\"routine\" is required"}`

**Problem:** Routines need to be wrapped in a `"routine"` key containing `"title"`, `"folder_id"`, and `"exercises"` array.

**Wrong:**
```json
{
  "name": "Day X",
  "description": "...",
  "exercises": [...]
}
```

**Correct:**
```json
{
  "routine": {
    "title": "Day X - Focus",
    "folder_id": 1812915,
    "exercises": [...]
  }
}
```

---

### 2. ❌ Invalid Set Type (Root Cause of Second Failure)
**Error:** `API Error: 400 - {"error":"\"routine.exercises[0].sets[1].type\" failed custom validation because Invalid set type: set"}`

**Problem:** Set type must be `"normal"` or `"warmup"`, NOT `"set"`.

**Wrong:**
```json
{
  "type": "set",
  "weight_kg": 60,
  "reps": 6
}
```

**Correct:**
```json
{
  "type": "normal",
  "weight_kg": 60,
  "reps": 6
}
```

---

## Required Fields for Each Exercise

```json
{
  "exercise_template_id": "91AF29E0",
  "superset_id": null,
  "rest_seconds": 60,
  "notes": "Exercise description and set scheme",
  "sets": [
    {
      "type": "warmup",                    // OR "normal"
      "weight_kg": 40,
      "reps": 12,
      "distance_meters": null,
      "duration_seconds": null,
      "custom_metric": null
    }
  ]
}
```

---

## Field Specifications

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `routine.title` | string | ✅ | Exercise name with sets/reps |
| `routine.folder_id` | number | ✅ | Always use: 1812915 |
| `exercise_template_id` | string | ✅ | 8-char hex OR UUID format |
| `superset_id` | null | ✅ | Always null (we don't use supersets) |
| `rest_seconds` | number | ✅ | Non-Core default 60; Core routines use 20 for all exercises; cluster in non-Core uses 30 |
| `notes` | string | ✅ | Exercise description with intensity notes |
| `type` | string | ✅ | **MUST be**: "warmup" or "normal" |
| `weight_kg` | number | ✅ | 0 for isometric/duration-based exercises |
| `reps` | number | ✅ | 0 for isometric/duration-based exercises |
| `duration_seconds` | number | ✅ | Use for isometric holds (e.g., 60 for 60-second hold) |

---

## Set Type Guidelines

### Valid Set Types (Per Hevy API Documentation)
Per https://api.hevyapp.com/docs/#/ - only these 4 types are officially supported:

```
"warmup"   - Light preparation set (before work sets)
"normal"   - Standard working set (most common)
"dropset"  - Weight reduced mid-exercise (6+6+8+10 pattern)
"failure"  - Set taken to muscular failure
```

### "warmup" Type
- First set in each exercise for non-Core routines (light, prep set)
- Example: `40kg x 12 reps` (before work sets)
- Often auto-populated from exercise history

### "normal" Type
- All working sets
- Standard strength/hypertrophy sets
- Example: `60kg x 6, 60kg x 7, 60kg x 8, 60kg x 8` (4 sets total)

### "dropset" Type
- Weight is reduced during the set
- Multiple sub-sets within one recorded set
- Notation: `35kg(6) → 30kg(6) → 25kg(8) → 20kg(10)`
- Rest between drops: 10-20 seconds

### "failure" Type
- Explicitly marked as taken to muscular failure
- Combined with weight/reps to track actual performance
- Used for intensity tracking

---

## Duration-Based Exercises (Isometric)

For exercises like "Sentadilla isométrica" (60-second hold):

```json
{
  "exercise_template_id": "c0ef33ba-3c50-4ced-a565-8caf48fff0ad",
  "sets": [
    {
      "type": "warmup",
      "weight_kg": 0,
      "reps": 0,
      "duration_seconds": 30       // ← Use duration instead
    },
    {
      "type": "normal",
      "weight_kg": 0,
      "reps": 0,
      "duration_seconds": 60
    }
  ]
}
```

---

## Quick Checklist Before Upload

- [ ] Routine wrapped in `"routine"` key?
- [ ] `folder_id` set to `1812915`?
- [ ] All set types are valid per Hevy API: `"warmup"`, `"normal"`, `"dropset"`, or `"failure"`?
- [ ] All exercise IDs validated against `exercise_mappings.md`?
- [ ] Non-Core routine: warmup sets included (usually first set)?
- [ ] Core routine: no warmup sets included?
- [ ] Duration-based exercises use `duration_seconds` with `weight_kg: 0, reps: 0`?
- [ ] `superset_id` is `null` for all exercises?
- [ ] Core routine: each exercise has 2 normal series and `rest_seconds` = 20?
- [ ] Non-Core routine: `rest_seconds` follows 60 default (or 30 for cluster)?
- [ ] Exercise notes include sets/reps/intensity info?

---

## Next Time: Use the Template

Instead of manually building JSON, copy `/template_routine.json` and modify only:
1. `routine.title` → Exercise name
2. Exercise array → Add/remove exercises from the template examples
3. `exercise_template_id` → Exercise IDs from `exercise_mappings.md`
4. Set weights and reps → Based on your workout plan

This prevents structural errors and ensures compliance with Hevy API constraints.
