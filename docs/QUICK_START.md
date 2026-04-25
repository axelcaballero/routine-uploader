# Routine Creation Quick Start

## The Two Critical Rules (Prevents 90% of API Errors)

### Rule #1: Structure
```
Root must be: { "routine": { ... } }
NOT: { "name": "...", "exercises": [...] }
```

### Rule #2: Set Types
```
"type": "warmup", "normal", "dropset", or "failure"
NEVER: "type": "set", "amrap", "rpe", or any other value
```

---

## 3-Step Workflow

### 1️⃣ Copy Template
```bash
cp TEMPLATE_routine.json input/dia_X_name.json
```

### 2️⃣ Edit These 3 Things
- `title`: "Día X – [Your Workout]"
- `exercise_template_id`: From `instructions.md`
- `weight_kg` and `reps`: Your actual workout numbers

### 3️⃣ Validate & Upload
```bash
./routines.sh validate input/dia_X_name.json
./routines.sh upload input/dia_X_name.json
```

### 📁 Check Your Routine Folders (Optional)
```bash
# See all your routine folders and which one is most recent
python get_recent_folder.py
```

This helps you verify the folder where routines will be uploaded before sending them.

---

## Common Mistakes & Fixes

| Issue | Wrong | Right |
|-------|-------|-------|
| Root key | `"exercises": [...]` | `"routine": { "exercises": [...] }` |
| Set type | `"type": "set"` | `"type": "normal"` (or "warmup", "dropset", etc.) |
| Folder ID | `"folder_id": 123` | `"folder_id": 1812915` |
| Exercise ID | Missing | From `instructions.md` |
| Isometric | `"reps": 60` | `"duration_seconds": 60, "reps": 0` |

---

## When You Hit an API Error

1. Check `API_STRUCTURE_GUIDE.md` for the error pattern
2. Look for `"type"` field - is it `"warmup"` or `"normal"`?
3. Verify `"routine"` key wraps everything
4. Check `exercise_template_id` exists in `instructions.md`

---

## What Gets Auto-Fixed

✅ Exercise warmup weights (from history)
✅ Routine metadata
✅ Exercise validation

❌ JSON structure errors (your responsibility)
❌ Set type errors (your responsibility)
❌ Exercise ID errors (state them, user provides)
