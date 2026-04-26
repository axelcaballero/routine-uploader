# Batch Routine Upload Guide

## Overview

The `batch_routine_uploader.py` tool safely handles importing multiple routines from the routine-extractor project, with built-in validation and safety checks for bulk operations.

---

## Safety Features

### 🛡️ Three-Phase Process

1. **Validation Phase** - Checks ALL routines before uploading ANY
   - Structure validation
   - Exercise ID validation  
   - Required fields check
   - Fails fast if any errors found

2. **Confirmation Phase** - Interactive approval (unless `--no-interactive`)
   - Lists all routines to be created
   - Shows exercise counts
   - Requires explicit confirmation

3. **Upload Phase** - Creates routines with progress tracking
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
venv/bin/python batch_routine_uploader.py extracted_routines.json --dry-run

# 2. (Optional) Verify/create folder for this session and apply to all routines
venv/bin/python batch_routine_uploader.py extracted_routines.json --dry-run --folder-title "HSF 15"

# 3. If validation passes, upload with confirmation
venv/bin/python batch_routine_uploader.py extracted_routines.json --folder-title "HSF 15"

# 4. Review summary and verify in Hevy app
```

### Command Options

```bash
# Validate only (no upload)
venv/bin/python batch_routine_uploader.py file.json --dry-run

# Upload with confirmation prompt (default, safest)
venv/bin/python batch_routine_uploader.py file.json

# Upload without confirmation (use with caution!)
venv/bin/python batch_routine_uploader.py file.json --no-interactive

# Skip warmup weight enhancement
venv/bin/python batch_routine_uploader.py file.json --no-enhance

# Apply one folder for this session (finds or creates it)
venv/bin/python batch_routine_uploader.py file.json --folder-title "HSF 15"
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
from batch_routine_uploader import BatchRoutineUploader

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
