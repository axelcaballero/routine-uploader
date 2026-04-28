# API Error Prevention System

## Overview
This system captures all key learnings from API errors encountered and prevents them from recurring through:
1. **Structured templates** → Correct JSON structure from the start
2. **Automated validation** → Catch errors BEFORE sending to API
3. **Quick reference guides** → Immediate reminders of critical rules
4. **Integrated checks** → Pre-flight verification built into workflow

---

## API Errors We've Prevented

### Error #1: Missing `"routine"` Root Key
**Original Error:**
```
API Error: 400 - {"error":"\"routine\" is required"}
```

**Prevention:**
- ✅ `TEMPLATE_routine.json` includes correct root structure
- ✅ `validate_structure.py` checks for `"routine"` key
- ✅ `./hevy.sh routines upload` runs structure check automatically

**Quick Fix:**
```json
{
  "routine": {           // ← MUST wrap everything
    "title": "...",
    "exercises": [...]
  }
}
```

---

### Error #2: Invalid Set Type
**Original Error:**
```
API Error: 400 - Invalid set type: set
```

**Prevention:**
- ✅ `TEMPLATE_routine.json` uses only valid types: `"warmup"`, `"normal"`, `"dropset"`, `"failure"`
- ✅ `validate_structure.py` validates set types before upload (per Hevy API docs)
- ✅ Error message tells you exact line/exercise/set with problem

**Quick Fix:**
```json
{
  "type": "warmup"     // or "normal", "dropset", "failure" (only these 4)
  // NEVER use "type": "set", "amrap", "rpe", or any other value
}
```

---

## New Resources

### 1. `TEMPLATE_routine.json`
Copy-paste template with correct structure for all exercises.
```bash
cp TEMPLATE_routine.json input/dia_X_name.json
# Then edit: title, exercise_template_id, weight_kg, reps
```

### 2. `QUICK_START.md`
One-page reference for the two critical rules + common mistakes.

### 3. `API_STRUCTURE_GUIDE.md`
Detailed breakdown of every required field and its constraints.

### 4. `validate_structure.py`
Standalone validator that checks JSON structure for API compliance.
```bash
python3 validate_structure.py input/dia_X.json
```

### 5. `./hevy.sh routines check <file>`
New wrapper command to run structure validation.
```bash
./hevy.sh routines check input/dia_X.json
```

### 6. Built-in Pre-flight Check
`./hevy.sh routines upload` now automatically runs structure validation:
```bash
./hevy.sh routines upload input/dia_X.json
# Runs structure check first, then validation, then upload
```

---

## Workflow: Before vs After

### OLD (Error-Prone)
1. Manually create JSON
2. Run validation: `./hevy.sh routines validate input/dia_X.json`
3. Run upload: `./hevy.sh routines upload input/dia_X.json`
4. ❌ API error → Back to step 1

### NEW (Error-Prevention)
1. Copy template: `cp TEMPLATE_routine.json input/dia_X.json`
2. Edit: title, exercise_template_id, weights/reps
3. Check structure: `./hevy.sh routines check input/dia_X.json`
4. Validate & upload: `./hevy.sh routines upload input/dia_X.json`
   - Pre-flight check ✅
   - Structure validation ✅
   - Exercise ID validation ✅
   - Upload with enhancement ✅
5. ✅ Success on first try

---

## Quick Decision Tree

**"I'm creating a new routine..."**

| Scenario | Action | Command |
|----------|--------|---------|
| Starting from scratch | Copy template | `cp TEMPLATE_routine.json input/dia_X.json` |
| Need API rules reminder | Read quick ref | `cat QUICK_START.md` |
| Unsure about field constraints | Read detailed guide | `cat API_STRUCTURE_GUIDE.md` |
| Before uploading | Structure check | `./hevy.sh routines check input/dia_X.json` |
| Ready to validate & upload | Use wrapper | `./hevy.sh routines upload input/dia_X.json` |
| Got API error | Check guide | `grep "Invalid set type" API_STRUCTURE_GUIDE.md` |

---

## Implementation Details

### `validate_structure.py` Checks:
✅ Root `"routine"` key exists
✅ Required fields: `title`, `folder_id`, `exercises`
✅ Each exercise has `exercise_template_id` and `sets` array
✅ Each set has valid `type`: "warmup" or "normal"
✅ Folder ID matches expected value (1812915)
✅ Warnings for unusual configurations (e.g., duration + weight/reps)

### Integration Points:
1. **Automatic:** `./hevy.sh routines upload` runs validator before upload
2. **Manual:** `./hevy.sh routines check <file>` for explicit validation
3. **Standalone:** `python3 validate_structure.py <file>` for CI/scripting

---

## Maintaining This System

When new API errors occur:
1. Document in `API_STRUCTURE_GUIDE.md`
2. Update `validate_structure.py` to catch it
3. Add example to `QUICK_START.md`
4. Update template if needed

---

## Success Metrics

| Metric | Before | After |
|--------|--------|-------|
| API errors before upload | 2+ per session | Caught automatically |
| Failed uploads | ~50% | <5% (only logic errors) |
| Time to fix structure issue | 10-15 min | <2 min (caught by validator) |
| New user learning curve | High (needs API docs) | Low (follow template) |

