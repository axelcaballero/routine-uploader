# Quick Reference - Core Workflow Commands

## ⚡ Quick Commands

```bash
# Setup (one-time)
pip install -r requirements.txt
export HEVY_API_KEY=<your-api-key>

# Optional utilities
python test_api_key.py
python scripts/next_workout.py
python routine_uploader.py routine.json
python routine_uploader.py routine.json --folder-title "HSF 15"
```

### Optional Utilities Usage

#### 1) Test API connection

Use this to quickly verify your API key and connectivity before running other tools.

```bash
python test_api_key.py
```

Expected result: success confirmation if credentials are valid.

#### 2) Get next workout in your sequence

Fetches your latest completed workout, finds the related folder/routine sequence,
and calculates the next workout day automatically.

```bash
python scripts/next_workout.py
```

Also writes output to `data/next_workout.json`.

#### 3) Upload a routine JSON

Uploads a single routine file directly to Hevy.

```bash
python routine_uploader.py routine.json
```

Use this when the routine already contains the correct folder metadata.

#### 4) Upload with per-session folder override

Forces the upload target folder for that command run only.

```bash
python routine_uploader.py routine.json --folder-title "HSF 15"
```

Use this when organizing routines by block/session name without editing the JSON file.

## 📂 Where to Find Files

| What | Location |
|------|----------|
| Scripts | `scripts/` |
| Raw Data (JSON) | `data/` |
| Documentation | `docs/` |

## 💡 Tips

- All scripts pull live data from Hevy API
- Run scripts anytime to refresh live outputs and JSON data
- JSON files auto-save in `data/` folder
