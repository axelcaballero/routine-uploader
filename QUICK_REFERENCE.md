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
