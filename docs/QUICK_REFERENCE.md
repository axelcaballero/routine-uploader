# Quick Reference - Progression Tracker Commands

## Run Scripts to Generate Data & Charts

```bash
# Bench Press Progression (160 sets tracked)
python scripts/bench_press_progression.py

# Squat Progression (101 sets tracked)
python scripts/squat_progression.py

# Shoulder Press Progression (183 sets tracked)
python scripts/shoulder_press_progression.py

# Analyze Squat Low Points
python scripts/analyze_squat_lowpoints.py
```

## Latest Workout RPE (Fast Commands)

### Get single workout RPE

```bash
# Get latest qualifying workout overall RPE (working sets only)
python hevy_cli.py workouts latest-rpe

# Get 2nd latest qualifying workout
python hevy_cli.py workouts latest-rpe --nth 2

# Get up to 5th latest (--nth 1-5, default is 1)
python hevy_cli.py workouts latest-rpe --nth 5
```

### Get all last 5 workouts at once

```bash
python hevy_cli.py workouts last-rpes
```

Applied filters for these commands:

- Only workouts titled Day/Dia 1 to Day/Dia 6
- Excludes core workouts
- Excludes focused forearms workouts
- Excludes focused calves workouts

Returns overall RPE calculated from working sets (warmups excluded). Fetches workouts directly from the live Hevy API.

## 📂 Where to Find Files

| What | Location |
|------|----------|
| Scripts | `scripts/` |
| Chart Images | `visualizations/` |
| Raw Data (JSON) | `data/` |
| Documentation | `PROGRESSION_TRACKER_README.md` |

## 📊 Exercise IDs (from Hevy API)

- Bench Press Barbell: `79D0BB3A`
- Squat Barbell: `D04AC939`
- Shoulder Press Dumbbell: `878CD1D0`

## 📈 2025 Progress Summary

| Exercise | Sets | Max | 1RM Est. | Period |
|----------|------|-----|----------|--------|
| Bench Press | 160 | 61.2 kg | 81.6 kg | Jan-Nov |
| Squat | 101 | 70.0 kg | 88.7 kg | Jan-Nov |
| Shoulder Press | 183 | 40.8 kg | 50.3 kg | Jan-Nov |

## 🛠 Setup (One-time)

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key (already configured)
export HEVY_API_KEY=<your-api-key>
```

## 💡 Tips

- All scripts pull live data from Hevy API
- Run scripts anytime to refresh visualizations and data
- JSON files auto-save in `data/` folder
- PNG charts auto-save in `visualizations/` folder
- Check `analyze_squat_lowpoints.py` for detailed strength analytics
