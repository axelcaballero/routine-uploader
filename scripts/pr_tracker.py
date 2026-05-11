#!/usr/bin/env python3
"""
PR Tracker - Detect personal records in qualifying Day 1-6 workouts.

Compares every working set in a workout against full prior exercise history
and reports volume PRs (weight × reps) per exercise.
"""

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

# Allow running from scripts/ directory or project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hevy_api_client import HevyAPIClient


# ---------------------------------------------------------------------------
# Filtering helpers (mirrors hevy_cli.py)
# ---------------------------------------------------------------------------

def _normalize(title: str) -> str:
    nfkd = unicodedata.normalize("NFKD", title)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()


def _is_allowed(title: str) -> bool:
    normalized = _normalize(title)
    if not re.search(r"\b(day|d[íi]a)\s+[1-6]\b", normalized):
        return False
    excluded = [
        "core", "abs", "abdominal",
        "forearm", "forearms", "antebrazo", "antebrazos",
        "calf", "calves", "pantorrilla", "pantorrillas", "gemelo", "gemelos",
    ]
    return not any(kw in normalized for kw in excluded)


# ---------------------------------------------------------------------------
# PR detection
# ---------------------------------------------------------------------------

def detect_prs(client: HevyAPIClient, workout: dict[str, Any]) -> list[dict[str, Any]]:
    """Return one entry per exercise that set a new volume PR in this workout.

    Within-session PRs (multiple sets each beating the previous best) are
    collapsed: only the best set that beat the all-time prior record is reported.
    """
    workout_date = str(workout.get("start_time", ""))[:10]
    results: list[dict[str, Any]] = []

    for ex in workout.get("exercises", []):
        ex_id = str(ex.get("exercise_template_id", ""))
        ex_title = str(ex.get("title", ""))

        working_sets = [
            (float(s.get("weight_kg") or 0), int(s.get("reps") or 0))
            for s in ex.get("sets", [])
            if s.get("type") != "warmup"
        ]
        if not working_sets:
            continue

        history = client.get_exercise_history(ex_id)
        prior_sets = [
            s for s in history.get("exercise_history", [])
            if not str(s.get("workout_start_time", "")).startswith(workout_date)
            and s.get("set_type") != "warmup"
        ]

        prior_max_vol = max(
            (float(s.get("weight_kg") or 0) * int(s.get("reps") or 0) for s in prior_sets),
            default=0.0,
        )

        best_pr: dict[str, Any] | None = None
        for w, r in working_sets:
            vol = w * r
            if vol > prior_max_vol:
                best_pr = {
                    "exercise": ex_title,
                    "weight_kg": round(w, 2),
                    "reps": r,
                    "volume": round(vol, 1),
                    "prev_best_volume": round(prior_max_vol, 1),
                }
                prior_max_vol = vol

        if best_pr:
            results.append(best_pr)

    return results


# ---------------------------------------------------------------------------
# Workout finder
# ---------------------------------------------------------------------------

def find_qualifying_workouts(client: HevyAPIClient, max_count: int = 6) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for page in range(1, 30):
        payload = client.list_workouts(page=page, page_size=10)
        workouts = payload.get("workouts", [])
        if not workouts:
            break
        for w in workouts:
            if _is_allowed(str(w.get("title", ""))):
                results.append(w)
                if len(results) >= max_count:
                    return results
        if len(workouts) < 10:
            break
    return results


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Detect personal records (volume) in qualifying Day 1-6 workouts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/pr_tracker.py              # PRs in latest qualifying workout\n"
            "  python scripts/pr_tracker.py --nth 3      # PRs in 3rd latest qualifying workout\n"
            "  python scripts/pr_tracker.py --all        # PRs for every workout in last full round\n"
            "  python scripts/pr_tracker.py --workout-id <id>"
        ),
    )
    parser.add_argument(
        "--nth",
        type=int,
        default=1,
        choices=range(1, 7),
        metavar="N",
        help="Which of the last 6 qualifying workouts to analyze (1=latest, default: 1)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Analyze all 6 workouts in the last round and report PRs per session",
    )
    parser.add_argument(
        "--workout-id",
        metavar="ID",
        help="Analyze a specific workout by its Hevy workout ID",
    )
    args = parser.parse_args()

    client = HevyAPIClient()

    if args.workout_id:
        workout = client.get_workout(args.workout_id)
        prs = detect_prs(client, workout)
        output = {
            "workout_id": workout.get("id"),
            "title": workout.get("title"),
            "date": str(workout.get("start_time", ""))[:10],
            "pr_count": len(prs),
            "personal_records": prs,
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return

    qualifying = find_qualifying_workouts(client, max_count=6)
    if not qualifying:
        print("No qualifying Day 1-6 workouts found.", file=sys.stderr)
        sys.exit(1)

    if args.all:
        sessions = []
        for w_meta in qualifying:
            workout = client.get_workout(str(w_meta.get("id", "")))
            prs = detect_prs(client, workout)
            sessions.append({
                "title": workout.get("title"),
                "date": str(workout.get("start_time", ""))[:10],
                "pr_count": len(prs),
                "personal_records": prs,
            })
        print(json.dumps(sessions, indent=2, ensure_ascii=False))
    else:
        nth_idx = args.nth - 1
        if nth_idx >= len(qualifying):
            print(f"Only {len(qualifying)} qualifying workouts available.", file=sys.stderr)
            sys.exit(1)
        workout = client.get_workout(str(qualifying[nth_idx].get("id", "")))
        prs = detect_prs(client, workout)
        output = {
            "workout_id": workout.get("id"),
            "title": workout.get("title"),
            "date": str(workout.get("start_time", ""))[:10],
            "pr_count": len(prs),
            "personal_records": prs,
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
