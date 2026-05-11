# Quick Reference - Progression Tracker Commands

## 🗂 Command Summary

| Command | Description |
|---------|-------------|
| `python hevy_cli.py workouts latest-rpe` | RPE from latest qualifying workout |
| `python hevy_cli.py workouts latest-rpe --nth N` | RPE from Nth latest workout (N = 1–6) |
| `python hevy_cli.py workouts latest-rpe --show-prs` | RPE + personal records from latest workout |
| `python hevy_cli.py workouts last-rpes` | RPE from all 6 workouts in last full round |
| `python hevy_cli.py workouts last-rpes --show-prs` | RPE + PRs for each of the last 6 sessions |
| `python hevy_cli.py workouts personal-records` | All-time volume PRs for every exercise in current roster |
| `python scripts/pr_tracker.py` | Detect PRs in latest qualifying workout |
| `python scripts/pr_tracker.py --nth N` | Detect PRs in Nth latest workout (N = 1–6) |
| `python scripts/pr_tracker.py --all` | Detect PRs across all 6 workouts in last round |
| `python scripts/pr_tracker.py --workout-id <id>` | Detect PRs in a specific workout by ID |

Filters applied to all workout commands: **Day/Dia 1–6 only**, excludes core, forearms, and calves workouts.

---

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

# Get up to 6th latest (--nth 1-6, default is 1)
python hevy_cli.py workouts latest-rpe --nth 6

# Also show personal records from that session
python hevy_cli.py workouts latest-rpe --show-prs
```

### Get complete round of last 6 workouts at once

```bash
# Track RPE from a complete round of main muscle training (Day 1-6)
python hevy_cli.py workouts last-rpes

# Include PR detection for each session
python hevy_cli.py workouts last-rpes --show-prs
```

Applied filters for these commands:

- Only workouts titled Day/Dia 1 to Day/Dia 6
- Excludes core workouts
- Excludes focused forearms workouts
- Excludes focused calves workouts

Returns overall RPE calculated from working sets (warmups excluded). Fetches workouts directly from the live Hevy API.

## 🏆 Personal Records

### All-time PRs for current exercise roster (Day 1-6)

```bash
# Show best volume set ever per exercise (across all history)
python hevy_cli.py workouts personal-records
```

### Detect PRs in recent workouts (standalone script)

```bash
# Latest qualifying workout
python scripts/pr_tracker.py

# Specific nth workout
python scripts/pr_tracker.py --nth 3

# Full round of last 6 workouts
python scripts/pr_tracker.py --all

# Specific workout by ID
python scripts/pr_tracker.py --workout-id <id>
```

PR detection is volume-based (weight × reps). Within-session records are collapsed to one per exercise.

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
