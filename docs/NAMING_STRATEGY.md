# Naming Strategy for Hevy Toolkit Files

## Project-Level Naming

Use these names for repo-level surfaces so the project reads as a broader Hevy toolkit rather than a routine-only uploader:

- Umbrella project name: `Hevy Training Toolkit`
- Generic CLI entrypoint: `hevy_cli.py`
- Shell wrapper: `hevy.sh`
- First-class command domains: `routines`, `folders`, `measurements`, `workouts`

Routine-specific scripts can stay routine-specific when they only solve routine workflows. The umbrella naming should appear on repo titles, quick-start docs, and project-level commands.

## Problem We're Preventing

**Anti-pattern:** When a requested file doesn't exist (e.g., `dia_7_espalda_hombro.json`), exploring what *does* exist and pivoting to it breaks the workflow clarity. This creates:
- Ambiguity about which exact routine was tested/uploaded
- Confusion about what was actually requested vs. what was executed
- Risk of uploading wrong data to wrong routine slots

**Solution:** Use explicit naming strategies that prevent naming collisions and make it impossible to accidentally use the wrong file.

---

## Naming Conventions by Folder

### `/input` Folder (Routine JSONs)
**Purpose:** Routines to be uploaded to Hevy API  
**Strategy:** Explicit, immutable naming based on what was requested

**Valid Patterns:**
```
dia_N_[name].json                   # Primary: Día 1-12, specific name
dia_N_[name]_v2.json                # Version suffix: explicitly marks iteration
dia_N_[name]_YYYYMMDD.json          # Date suffix: tracks when created
dia_N_[name]_HASH.json              # Hash suffix: content-based identifier
```

**Examples:**
```
dia_7_espalda_hombro.json           # Original request
dia_7_espalda_hombro_v2.json        # Revised version
dia_7_espalda_hombro_20251122.json  # Dated version
```

**Rule:** If `dia_7_espalda_hombro.json` is requested and doesn't exist:
- ❌ DON'T check if `dia_11_hombro_espalda.json` exists
- ✅ DO fail explicitly: "dia_7_espalda_hombro.json not found. Create it?"

---

### `/data` Folder (Workout Data/Analysis)
**Purpose:** Store workout history, progression data, notes  
**Strategy:** Timestamp + content type + suffix to prevent accidental overwrites

**Valid Patterns:**
```
[exercise]_data_YYYY-MM-DD.json     # Daily snapshots
[exercise]_data_v1.json             # Version 1
[exercise]_data_v2_backup.json      # Versioned backup
[exercise]_data_HASH.json           # Content hash
hfs/[exercise]_YYYYMMDD/            # Folder per day (HFS = Historical File Structure)
```

**Examples:**
```
squat_data_2025-11-22.json          # Today's squat data
bench_press_data_v2.json            # Revised bench data
shoulder_press_data_v2_backup.json  # Backup before changes
```

**Rule:** Always append version/date/hash suffix:
- ❌ DON'T: `squat_data.json` (overwrites on every save)
- ✅ DO: `squat_data_2025-11-22.json` (new file each day)
- ✅ DO: `squat_data_v2.json` (explicit version marker)

---

### `/analysis` Folder (Analysis Results)
**Purpose:** Generated reports, visualizations, metrics  
**Strategy:** Timestamp + analysis type to track evolution

**Valid Patterns:**
```
[metric]_analysis_YYYY-MM-DD.json   # Daily analysis
[metric]_progression_v1.json        # Versioned progression
[metric]_report_HASH.json           # Content-addressed report
```

**Examples:**
```
max_strength_analysis_2025-11-22.json
volume_progression_v2.json
```

---

## Enforcement Rules

### For Agent Operations:
1. **Explicit File Requests:** If file X is requested and doesn't exist, fail with clear message:
   ```
   ❌ File not found: dia_7_espalda_hombro.json
   Available alternatives: [list if helpful]
   Create it? (Provide explicit yes/no, don't pivot)
   ```

2. **Version Control:** If updating an existing file, use suffix:
   ```
   ✅ dia_7_espalda_hombro.json exists
   Creating: dia_7_espalda_hombro_v2.json (preserves original)
   ```

3. **No Implicit Substitutions:** Never silently swap `dia_7` for `dia_11` because they're "similar"
   - This violates explicit intent
   - Creates ambiguity in what was actually tested
   - Breaks auditability

### For Users:
1. Provide complete filename or clear naming pattern upfront
2. If updates needed, specify: `v2`, date suffix, or new folder
3. If unsure about naming, ask before creating

---

## Quick Reference

| Scenario | ✅ Do This | ❌ Don't Do This |
|----------|-----------|-----------------|
| Create new routine | `dia_7_espalda_hombro.json` | `routine.json` |
| Update existing routine | `dia_7_espalda_hombro_v2.json` | Overwrite `dia_7_espalda_hombro.json` |
| Daily data snapshot | `squat_data_2025-11-22.json` | `squat_data.json` |
| File not found | Fail + ask | Check alternatives + pivot |
| Similar files exist | List them, ask user | Use similar one instead |

---

## Implementation Checklist

- [ ] All `/input` routines follow `dia_N_[name]` or `dia_N_[name]_vX` pattern
- [ ] All `/data` files include date suffix (YYYY-MM-DD) or version suffix
- [ ] All `/analysis` files timestamped or versioned
- [ ] Agent explicitly fails if requested file not found (no silent pivoting)
- [ ] New files use suffixes to prevent overwrites

---

## See Also
- `QUICK_START.md` - Workflow reference
- `TEMPLATE_routine.json` - Routine structure
- `instructions.md` - Exercise mappings
