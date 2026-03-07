# Manual Mode Routine Upload (No Copilot)

This file documents how to upload routines yourself from terminal only.

## 1) Prerequisites

- You are in repo root: `d:/DEV/sandbox/routine-uploader`
- `.env` contains a valid `HEVY_API_KEY`
- Python venv exists at `.venv`

## 2) Activate Python Environment

### Bash Activation

```bash
source .venv/Scripts/activate
```

### PowerShell Activation

```powershell
.\.venv\Scripts\Activate.ps1
```

## 3) Paste Routine Text Into a File

Use one file per routine or one file with multiple routines.

### Bash Paste

```bash
mkdir -p input
cat > input/dx_raw.txt <<'EOF'
Dia X - NAME
MUSCLE 5
Ejercicio 1 - 4x10rep. (moderado peso 80%)
1-Exercise name
EOF
```

### PowerShell Paste

```powershell
New-Item -ItemType Directory -Force input | Out-Null
@'
Dia X - NAME
MUSCLE 5
Ejercicio 1 - 4x10rep. (moderado peso 80%)
1-Exercise name
'@ | Set-Content -Path input/dx_raw.txt -Encoding utf8
```

## 4) Parse Text to JSON (Batch Format)

```bash
python routine_text_parser.py input/dx_raw.txt -o input/dx_parsed.json --mappings instructions.md
```

Output format is batch JSON:

- root key: `routines`
- each item: `{ "routine": { ... } }`

## 5) Check Missing Exercise IDs

### Bash Missing-ID Check

```bash
grep -n '"exercise_template_id": ""' input/dx_parsed.json || echo "No missing IDs"
```

### PowerShell Missing-ID Check

```powershell
if (-not (Select-String -Path input/dx_parsed.json -Pattern '"exercise_template_id": ""')) {
  "No missing IDs"
}
```

If you have missing IDs, search available mappings:

```bash
python exercise_validator.py --list | grep -i "keyword"
```

## 6) Validate + Dry-Run Upload (Recommended)

Because parser output is batch JSON, validate and dry-run with batch uploader:

```bash
python batch_routine_uploader.py input/dx_parsed.json --dry-run --folder-title "HSF 15"
```

## 7) Live Upload

```bash
python batch_routine_uploader.py input/dx_parsed.json --folder-title "HSF 15"
```

Notes:

- `--folder-title "HSF 15"` is session-only and creates folder if missing.
- Remove `--folder-title` if you want to keep each routine `folder_id` from file.

## 8) Optional Post-Upload Verification

Use routine ID shown in uploader output:

```bash
python -c "from hevy_api_client import HevyAPIClient; rid='PASTE_ROUTINE_ID'; c=HevyAPIClient(); r=c.get_routine(rid).get('routine', {}); print('title:', r.get('title')); print('folder_id:', r.get('folder_id')); print('exercises:', len(r.get('exercises', [])))"
```

## 9) Single-Routine Alternative (If You Prefer `routine_uploader.py`)

Extract first routine from parsed batch to a single routine JSON:

```bash
python - <<'PY'
import json
src = 'input/dx_parsed.json'
dst = 'input/dx_single.json'
with open(src, encoding='utf-8') as f:
    data = json.load(f)
with open(dst, 'w', encoding='utf-8') as f:
    json.dump(data['routines'][0], f, indent=2, ensure_ascii=False)
print('Saved', dst)
PY
```

Then run single-file validation/upload:

```bash
python validate_structure.py input/dx_single.json
python exercise_validator.py input/dx_single.json
python routine_uploader.py input/dx_single.json --dry-run --folder-title "HSF 15"
python routine_uploader.py input/dx_single.json --folder-title "HSF 15"
```

## 10) Core Routine Reminder (Current Project Policy)

- Core routines: no warmup sets
- Core routines: exactly 2 normal series per exercise
- Core routines: `rest_seconds` is 20
