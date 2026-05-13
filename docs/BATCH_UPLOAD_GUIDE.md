# Batch Routine Upload Guide

## Overview

The `batch_routine_uploader.py` tool safely handles importing multiple routines from the routine-extractor project, with built-in validation and safety checks for bulk operations.

⚠️ **IMPORTANT:** Always validate routines against [ROUTINE_CREATION_RULES.md](ROUTINE_CREATION_RULES.md) BEFORE uploading. See [Pre-Upload Validation](#pre-upload-validation) section below.

---

## Pre-Upload Validation

**REQUIRED STEP:** Before using batch_routine_uploader.py, validate all routines against project rules.

### Why This Matters
Past uploads violated rules (missing warmup sets, incorrect rest times) because rule validation was skipped. This required emergency API updates to fix already-uploaded routines. **Prevention is better than retroactive fixes.**

### Validation Steps

1. **Read Complete Rules**
   ```bash
   # Review all 205 lines
   cat ROUTINE_CREATION_RULES.md
   ```

2. **Run Rules Compliance Validator**
   ```bash
   python scripts/validate_rules_compliance.py input/dia_*.json
   ```
   
   This checks:
   - ✅ Rep ranges use maximum value
   - ✅ Exercises requiring doubled reps (11 specific exercises)
   - ✅ Warmup sets present (12 or 24 reps)
   - ✅ No RPE fields
   - ✅ Correct rest_seconds (60 default, exceptions noted)
   - ✅ Valid set types
   - ✅ Core routine special rules

3. **Review Pre-Upload Checklist**
   ```bash
   cat PRE_UPLOAD_CHECKLIST.md
   ```

4. **Only After All Checks Pass**
   ```bash
   python scripts/batch_routine_uploader.py --batch-file input/routines.json
   ```

---

## Safety Features

### 🛡️ Four-Phase Process

1. **Rules Validation Phase** - ⚠️ **MANUAL STEP** (run validate_rules_compliance.py)
   - Validates against ROUTINE_CREATION_RULES.md
   - Checks warmup sets, rest times, rep doubling, etc.
   - **Must pass before proceeding**

2. **Structure Validation Phase** - Checks ALL routines before uploading ANY
   - Structure validation
   - Exercise ID validation  
   - Required fields check
   - Fails fast if any errors found

3. **Confirmation Phase** - Interactive approval (unless `--no-interactive`)
   - Lists all routines to be created
   - Shows exercise counts
   - Requires explicit confirmation

4. **Upload Phase** - Creates routines with progress tracking
   - Individual error handling per routine
   - Continues on single failure
   - Detailed summary at end

---

## Input Formats

### Batch Format (Multiple Routines)
```json
{
  "routines": [
    {
      "routine": {
            "title": "Day 1 - Chest and Shoulders",
            "folder_id": 1234567,
        "exercises": [...]
      }
    },
    {
      "routine": {
            "title": "Day 2 - Back + Core",
            "folder_id": 1234567,
        "exercises": [...]
      }
    }
  ]
}
```

### Single Routine Format (Also Accepted)
```json
{
  "routine": {
      "title": "Day 1 - Chest and Shoulders",
      "folder_id": 1234567,
    "exercises": [...]
  }
}
```

`folder_id` can be overridden per upload session using `--folder-title`.

---

## Usage

### Recommended Workflow (Safest)

```bash
# 1. Dry run first - validate without uploading
venv/bin/python scripts/batch_routine_uploader.py extracted_routines.json --dry-run

# 2. (Optional) Verify/create folder for this session and apply to all routines
venv/bin/python scripts/batch_routine_uploader.py extracted_routines.json --dry-run --folder-title "HSF 15"

# 3. If validation passes, upload with confirmation
venv/bin/python scripts/batch_routine_uploader.py extracted_routines.json --folder-title "HSF 15"

# 4. Review summary and verify in Hevy app
```

### Command Options

```bash
# Validate only (no upload)
venv/bin/python scripts/batch_routine_uploader.py file.json --dry-run

# Upload with confirmation prompt (default, safest)
venv/bin/python scripts/batch_routine_uploader.py file.json

# Upload without confirmation (use with caution!)
venv/bin/python scripts/batch_routine_uploader.py file.json --no-interactive

# Skip warmup weight enhancement
venv/bin/python scripts/batch_routine_uploader.py file.json --no-enhance

# Apply one folder for this session (finds or creates it)
venv/bin/python scripts/batch_routine_uploader.py file.json --folder-title "HSF 15"
```

---

## Example Output

### Validation Phase
```
======================================================================
🔍 VALIDATION PHASE - Checking 12 routine(s)
======================================================================

[1/12] Día 1 – Pecho y Hombro
   ✅ VALID

[2/12] Día 2 – Espalda + Core
   ✅ VALID

[3/12] Día 3 – Pierna
   ❌ FAILED - 2 error(s)
      • Exercise: Exercise ID 'INVALID123' not found in exercise_mappings.md
      • Structure: Invalid set type: drop_set (should be dropset)

...

✅ All 11 routine(s) passed validation!
⚠️  1 routine(s) failed validation
Fix errors before proceeding.
```

### Confirmation Prompt
```
======================================================================
⚠️  READY TO UPLOAD 11 ROUTINE(S)
======================================================================

Routines to be created:
   1. Día 1 – Pecho y Hombro (8 exercises)
   2. Día 2 – Espalda + Core (6 exercises)
   3. Día 4 – Bíceps y Tríceps (8 exercises)
   ...

Proceed with upload? [y/N]: 
```

### Upload Phase
```
======================================================================
📤 UPLOAD PHASE - Creating 11 routine(s)
======================================================================

[1/11] Día 1 – Pecho y Hombro
   ✓ Enhanced with historical data
   ✅ Created! ID: 0941346a-33d8-48d0-bd7a-880e8171c1a7

[2/11] Día 2 – Espalda + Core
   ✓ Enhanced with historical data
   ✅ Created! ID: 1e19bb55-73df-4088-a3ef-09423439aefc

...
```

### Summary
```
======================================================================
📊 BATCH UPLOAD SUMMARY
======================================================================

Total routines: 12
✅ Successful:  11
❌ Failed:      1
⏭️  Skipped:     0

✅ Successfully uploaded:
   [1] Día 1 – Pecho y Hombro (ID: 0941346a-33d8-48d0-bd7a-880e8171c1a7)
   [2] Día 2 – Espalda + Core (ID: 1e19bb55-73df-4088-a3ef-09423439aefc)
   ...

❌ Failed uploads:
   [3] Día 3 – Pierna
      Error: API Error: 400 - Invalid exercise ID
```

---

## Integration with routine-extractor

### Expected Workflow

1. **Extract routines from PDF**
   ```bash
   cd ../routine-extractor
   python extract_routines.py workout_program.pdf
   # Outputs: extracted_routines.json
   ```

2. **Validate extraction**
   ```bash
   cd ../routine-uploader
   venv/bin/python batch_routine_uploader.py \
       ../routine-extractor/extracted_routines.json --dry-run --folder-title "HSF 15"
   ```

3. **Fix any validation errors** in the extracted file

---

## Handling Missing Exercises

### When Exercise IDs Are Not Found

If validation fails with "NOT FOUND IN instructions.md" errors:

**❌ DO NOT:**
- Invent or guess exercise IDs
- Create placeholder IDs
- Automatically search and assign IDs

**✅ DO:**
1. Note the missing Spanish exercise names
2. Manually look up the correct exercise in Hevy app or API
3. Add the mapping to `instructions.md` following the format:
   ```
   * Spanish Name es English Equivalent | ACTUAL_HEX_ID
   ```
4. Re-run validation after updating instructions.md

### Fuzzy Matching for Minor Variations

**IMPORTANT:** The conversion system uses **fuzzy matching (≥85% similarity)** to handle minor variations between PDF extraction and instructions.md:

**Common variations automatically handled:**
- Plural differences: "Peso muerto con mancuerna" → "Peso muerto con mancuernas"
- Accent differences: "Fondos en maquina" → "Fondos en máquina"
- Case differences: "Dominadas con apoyo" → "Dominadas con Apoyo"
- Minor typos: "Martillo dobles" → "Martillos dobles"
- Word additions: "Alternado con mancuerna" → "Curl Alternado con mancuerna"

**Why fuzzy matching:**
- PDF extraction may have minor text variations
- Spanish plural/singular inconsistencies
- Accent marks may be missing or added
- Reduces manual mapping work for near-identical exercises

**When fuzzy matching fails (<85% similarity):**
- Completely different exercise names
- Abbreviated vs full names
- Names with multiple possible interpretations
- In these cases, manual mapping in instructions.md is required

**Technical Details:**
- Uses Python's `difflib.get_close_matches()` 
- Cutoff threshold: 0.85 (85% similarity)
- Only matches if confidence is high enough
- Logs all fuzzy matches for transparency

**Example Workflow:**
```bash
# 1. Validation fails with missing exercises
venv/bin/python batch_routine_uploader.py file.json --dry-run
# Output: ❌ Pullover con mancuernas - NOT FOUND IN instructions.md

# 2. Look up exercise in Hevy (use list command or app)
python exercise_validator.py --list | grep -i pullover

# 3. Add to instructions.md
echo "* Pullover con mancuernas es Dumbbell Pullover | EA42E2F4" >> instructions.md

# 4. Retry validation
venv/bin/python batch_routine_uploader.py file.json --dry-run
```

**Why This Matters:**
- Maintains data integrity by using real Hevy exercise IDs
- Prevents API errors from invalid IDs
- Builds reusable exercise mappings in instructions.md
- Follows manifesto principle: "No debes asumir ids si no encuentras equivalencias"

4. **Upload when ready**
   ```bash
   venv/bin/python batch_routine_uploader.py \
       ../routine-extractor/extracted_routines.json --folder-title "HSF 15"
   ```

---

## Error Handling

### Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `Invalid format` | Wrong JSON structure | Use batch format `{"routines": [...]}` |
| `Exercise ID not found` | ID missing from exercise_mappings.md | Add exercise mapping or use interactive validator |
| `Structure: Invalid set type` | Wrong set type name | Use `dropset` not `drop_set`, only warmup/normal/dropset/failure |
| `Missing routine title` | No title field | Add `"title": "Día X – ..."` |
| `API Error: 400` | Invalid field values | Check API_STRUCTURE_GUIDE.md |

### What Happens on Partial Failure?

- **Validation fails**: No routines uploaded, fix errors and retry
- **Upload fails for 1 routine**: Other routines continue, summary shows what succeeded/failed
- **User cancels**: No routines uploaded, can retry later

---

## Safety Checklist

Before uploading 6-12 routines:

- [ ] Run with `--dry-run` first to validate
- [ ] Review all validation errors and warnings
- [ ] Check exercise IDs against `exercise_mappings.md`
- [ ] Verify routine titles follow "Día X – Name" pattern
- [ ] Verify session folder with `--folder-title` (or confirm each routine `folder_id`)
- [ ] Have backup of extracted file
- [ ] Start with small batch (1-3 routines) to test
- [ ] Use interactive mode for first upload

---

## Advanced Usage

### Testing with Subset

Extract specific routines to test:
```python
import json

# Load all routines
with open('extracted_routines.json') as f:
    data = json.load(f)

# Save first 3 for testing
test_batch = {"routines": data['routines'][:3]}
with open('test_batch.json', 'w') as f:
    json.dump(test_batch, f, indent=2)
```

```bash
# Upload test batch
venv/bin/python batch_routine_uploader.py test_batch.json
```

### Programmatic Usage

```python
from scripts.batch_routine_uploader import BatchRoutineUploader

uploader = BatchRoutineUploader()

# Load routines
routines = uploader.load_batch_file('extracted_routines.json')

# Validate
valid, invalid = uploader.validate_batch(routines)

# Upload if all valid
if not invalid:
    results = uploader.upload_batch(valid, dry_run=False, interactive=False)
    uploader.print_summary(results)
```

---

## Files Created

- `batch_routine_uploader.py` - Main batch upload script
- `docs/BATCH_UPLOAD_GUIDE.md` - This documentation

---

## See Also

- `ROUTINE_CREATION_RULES.md` - Rules for individual routines
- `API_STRUCTURE_GUIDE.md` - API format requirements
- `VALIDATION_SYSTEM_COMPLETE.md` - Validation details
- `ERROR_PREVENTION_SYSTEM.md` - Error handling guide
