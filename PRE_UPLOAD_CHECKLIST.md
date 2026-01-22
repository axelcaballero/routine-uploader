# Pre-Upload Validation Checklist

## Purpose
This checklist MUST be reviewed before uploading ANY routine to Hevy API. It prevents rule violations and ensures consistency across all routines.

## Critical Rules from ROUTINE_CREATION_RULES.md

### ✅ Rule 1: Rep Ranges Use Maximum Value
- **Requirement:** When spec says "4x6-8rep", use 8 reps, not 6
- **Check:** All exercises with range notation use the highest number
- **Example:** 3x12-15 → 15 reps, not 12

### ✅ Rule 2: "Duplicar repeticiones" Means 2x Reps
- **Requirement:** When exercise has "Duplicar repeticiones" flag, double ALL reps (warmup AND normal)
- **Check:** Affected exercises have 2x the specified reps
- **Example:** 4x12rep with flag → 24 reps per set

### ✅ Rule 3: 11 Exercises Always Get Doubled
- **Requirement:** These exercises ALWAYS double reps (even without explicit flag):
  - **Hombro:** Press militar con mancuerna, Elevaciones laterales con mancuerna, Elevaciones frontales con mancuerna, Elevaciones posteriores con mancuerna
  - **Bíceps:** Curl concentrado con mancuerna, Curl alternado con mancuerna, Curl martillo con mancuerna, Curl con mancuerna (supino)
  - **Tríceps:** Extensión de tríceps por encima de la cabeza con mancuerna, Extensiones de tríceps inclinado con mancuerna, Patada de tríceps con mancuerna
- **Check:** All 11 exercises have doubled reps in your routine
- **Example:** Curl alternado 3x10 → 20 reps per set

### ✅ Rule 4: Warmup Sets ALWAYS First
- **Requirement:** EVERY exercise starts with a warmup set
- **Warmup Reps:** 12 reps (or 24 reps if exercise requires doubling)
- **Check:** First set is type "warmup"
- **Total Sets:** Spec says "4x12" = 5 total sets (1 warmup + 4 normal)

### ✅ Rule 5: NO RPE in Routines
- **Requirement:** The "rpe" field is ONLY for workout logging, NEVER for routine templates
- **Check:** No "rpe" key exists in any exercise object
- **See:** API_STRUCTURE_GUIDE.md Section 3

### ✅ Rule 6: Default Rest Time is 60 Seconds
- **Requirement:** Unless specified otherwise, all exercises have `rest_seconds: 60`
- **Exceptions:**
  - **Supersets:** 0 seconds for all except last exercise (120 seconds)
  - **Sistema bulgaro with "10-30seg":** 30 seconds
  - **Notes say "10-20seg. de recuperación":** 20 seconds
  - **Core routines:** 20 seconds
- **Check:** Verify rest_seconds matches these rules
- **Common mistake:** Using 120 seconds by default (WRONG!)

### ✅ Rule 7: Core Routine Special Rules
- **When:** Routine name contains "Core"
- **Requirements:**
  - 2 series (not counting warmup)
  - 20 seconds rest (`rest_seconds: 20`)
  - 30 seconds duration (`duration_seconds: 30`) when time-based
- **Check:** Core routines follow these specific overrides

### ✅ Rule 8: Exercise IDs Must Be Hex or UUID
- **Requirement:** exercise_template_id must be 8-char uppercase hex (e.g., 50DFDFAB) or UUID
- **Never:** Spanish text, English names, or made-up values
- **Check:** All IDs exist in instructions.md mapping

### ✅ Rule 9: Set Types Must Be Valid
- **Allowed:** "normal", "warmup", "failure", "dropset"
- **Never:** "working", "main", "regular"
- **Check:** All sets use valid type strings

### ✅ Rule 10: Notes Contain Original Spec
- **Requirement:** Preserve original rep notation and details in notes field
- **Example:** "4x6-8rep. (85% o más)"
- **Check:** Notes accurately reflect PDF spec

## Pre-Upload Validation Process

### Step 1: Read ROUTINE_CREATION_RULES.md
Before creating ANY routine, read the complete rules file (lines 1-205)

### Step 2: Validate Structure
Run `validate_structure.py` to check JSON format

### Step 3: Validate Exercise IDs
Verify all exercise_template_id values exist in instructions.md

### Step 4: Validate Rules Compliance
Run the new `validate_rules_compliance.py` script:
- ✅ Rep ranges use max value
- ✅ Doubling rules applied correctly
- ✅ Warmup sets present (12 or 24 reps)
- ✅ No RPE fields
- ✅ Correct rest_seconds (60 default, exceptions noted)
- ✅ Core routine special rules
- ✅ Valid set types
- ✅ Notes preserved

### Step 5: Manual Review
- Review output JSON files visually
- Spot-check 2-3 exercises per routine
- Verify against original PDF

### Step 6: Test Upload (Optional)
- Upload to test folder first
- Verify in Hevy app
- Check all sets, reps, rest times

### Step 7: Production Upload
Only after ALL checks pass, upload to production folder

## Common Mistakes to Avoid

❌ **Skipping warmup sets** - Every exercise needs a warmup!
❌ **Using 120 seconds rest by default** - Default is 60!
❌ **Forgetting to double reps** - Check all 11 exercises + explicit flags
❌ **Adding RPE to routines** - Only for workout logs!
❌ **Using wrong rep value in ranges** - Always use the MAXIMUM!
❌ **Missing notes field** - Preserve original spec!
❌ **Wrong set types** - Use "normal", not "working"!

## Emergency Fixes

If routines are already uploaded with violations:

### Fix Missing Warmup Sets
Use `add_warmup_sets.py` to retrofit warmup sets via API

### Fix Wrong Rest Times
Use `fix_rest_times.py` to update rest_seconds via API

### Fix Wrong Reps
Must update routine via API PUT endpoint with corrected sets

## Permanent Documentation

This checklist is saved permanently. Review it:
- At start of EVERY chat session involving routine creation
- Before ANY batch upload
- When debugging why uploaded routines are incorrect

**Last Updated:** 2025 (after discovering missing warmup sets and incorrect rest times in Diciembre batch)
