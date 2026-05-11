#!/usr/bin/env python3
"""Umbrella CLI for Hevy training workflows."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from contextlib import contextmanager
from pathlib import Path
from statistics import mean
from typing import Any, Callable, Iterator, Sequence

import batch_routine_uploader
import create_new_folder
import exercise_validator
import folder_manager
import get_recent_folder
import routine_uploader
import test_api_key
import validate_structure
from hevy_api_client import HevyAPIClient


@contextmanager
def _patched_argv(argv: Sequence[str]) -> Iterator[None]:
    original_argv = sys.argv[:]
    sys.argv = list(argv)
    try:
        yield
    finally:
        sys.argv = original_argv


def _run_entrypoint(entrypoint: Callable[[], None], argv: Sequence[str]) -> int:
    with _patched_argv(argv):
        try:
            entrypoint()
        except SystemExit as exc:
            code = exc.code
            return 0 if code is None else int(code)
    return 0


def _print_planned_capability(domain: str) -> int:
    print(f"{domain} commands are reserved for the upcoming Hevy toolkit expansion.")
    print("Planned scope includes body measurements management and workout retrieval/analysis.")
    return 0


def _print_json(data: Any) -> int:
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


def _load_json_payload(json_path: str) -> dict[str, Any]:
    with open(json_path, "r", encoding="utf-8") as file_handle:
        data = json.load(file_handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object in {json_path}")
    return data


def _safe_cell(value: str) -> str:
    return value.replace("|", "/").strip()


def _load_exercise_name_index(instructions_path: str = "exercise_mappings.md") -> dict[str, tuple[str, str]]:
    """Build exercise ID -> (source exercise name, Hevy exercise name) index from exercise_mappings.md."""
    exercise_index: dict[str, tuple[str, str]] = {}
    pattern = re.compile(r"^\*\s+(.+?)\s+es\s+(.+?)\s+\|\s+([A-Za-z0-9-]+)")

    try:
        with open(instructions_path, "r", encoding="utf-8") as file_handle:
            for raw_line in file_handle:
                match = pattern.match(raw_line.strip())
                if not match:
                    continue

                source_name = match.group(1).strip()
                hevy_name = match.group(2).strip()
                exercise_id = match.group(3).strip().lower()
                exercise_index[exercise_id] = (source_name, hevy_name)
    except FileNotFoundError:
        return {}

    return exercise_index


def _extract_source_name(exercise: dict[str, Any], exercise_index: dict[str, tuple[str, str]]) -> str:
    exercise_id = str(exercise.get("exercise_template_id", "")).strip().lower()
    notes = str(exercise.get("notes", "")).strip()

    if notes:
        # Exercise notes convention starts with source exercise name before the first hyphen.
        source_from_notes = notes.split(" - ", 1)[0].strip()
        if source_from_notes:
            return source_from_notes

    indexed = exercise_index.get(exercise_id)
    if indexed:
        return indexed[0]
    return exercise_id or "Unknown"


def _extract_hevy_name(exercise: dict[str, Any], exercise_index: dict[str, tuple[str, str]]) -> str:
    exercise_id = str(exercise.get("exercise_template_id", "")).strip().lower()
    indexed = exercise_index.get(exercise_id)
    if indexed:
        return indexed[1]
    return exercise_id or "Unknown"


def _collapse_reps_for_cluster(reps_list: list[int]) -> str:
    grouped: list[tuple[int, int]] = []
    for rep in reps_list:
        if grouped and grouped[-1][0] == rep:
            grouped[-1] = (rep, grouped[-1][1] + 1)
        else:
            grouped.append((rep, 1))
    return " + ".join(f"{count}x{rep}" for rep, count in grouped)


def _format_sets_x_reps(exercise: dict[str, Any]) -> str:
    sets = exercise.get("sets", [])
    if not isinstance(sets, list):
        return "-"

    warmup_reps = [
        int(series.get("reps"))
        for series in sets
        if isinstance(series, dict)
        and series.get("type") == "warmup"
        and isinstance(series.get("reps"), int)
    ]

    normal_reps = [
        int(series.get("reps"))
        for series in sets
        if isinstance(series, dict)
        and series.get("type") == "normal"
        and isinstance(series.get("reps"), int)
    ]

    if not warmup_reps and not normal_reps:
        return "-"

    notes = str(exercise.get("notes", "")).lower()
    is_cluster = "cluster" in notes
    normal_part = ""
    if normal_reps:
        if is_cluster:
            normal_part = f"cluster: {_collapse_reps_for_cluster(normal_reps)}"
        elif len(set(normal_reps)) == 1:
            normal_part = f"{len(normal_reps)}x{normal_reps[0]}"
        else:
            normal_part = " + ".join(f"1x{rep}" for rep in normal_reps)

    warmup_part = _collapse_reps_for_cluster(warmup_reps) if warmup_reps else ""

    if warmup_part and normal_part:
        return f"{warmup_part} + {normal_part}"
    if warmup_part:
        return warmup_part
    return normal_part


def _print_routine_summary_table(routine_file: str, instructions_path: str = "exercise_mappings.md") -> int:
    payload = _load_json_payload(routine_file)
    routine = payload.get("routine")
    if not isinstance(routine, dict):
        raise ValueError(f"Invalid routine JSON: missing 'routine' object in {routine_file}")

    routine_note = str(routine.get("notes", "")).strip()

    exercises = routine.get("exercises", [])
    if not isinstance(exercises, list):
        raise ValueError(f"Invalid routine JSON: 'routine.exercises' must be a list in {routine_file}")

    exercise_index = _load_exercise_name_index(instructions_path)

    print("| # | source exercise name | Hevy excercise name | Sets x Reps |")
    print("|---|---|---|---|")

    for index, exercise in enumerate(exercises, start=1):
        if not isinstance(exercise, dict):
            continue
        source_name = _safe_cell(_extract_source_name(exercise, exercise_index))
        hevy_name = _safe_cell(_extract_hevy_name(exercise, exercise_index))
        sets_x_reps = _safe_cell(_format_sets_x_reps(exercise))
        print(f"| {index} | {source_name} | {hevy_name} | {sets_x_reps} |")

    print("")
    if routine_note:
        print(f"Routine note: {routine_note}")
    else:
        print("Routine note: (none)")

    return 0


def _measurement_fields_from_args(args: argparse.Namespace) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for field_name in HevyAPIClient.body_measurement_fields():
        field_value = getattr(args, field_name, None)
        if field_value is not None:
            payload[field_name] = field_value
    return payload


def _build_measurement_payload(args: argparse.Namespace, *, include_date: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    if getattr(args, "json_file", None):
        payload.update(_load_json_payload(args.json_file))
    payload.update(_measurement_fields_from_args(args))

    if include_date and getattr(args, "date", None):
        payload["date"] = args.date
    return payload


def _add_measurement_field_arguments(parser: argparse.ArgumentParser) -> None:
    for field_name in HevyAPIClient.body_measurement_fields():
        parser.add_argument(f"--{field_name.replace('_', '-')}", dest=field_name, type=float)


def _handle_measurements_command(args: argparse.Namespace) -> int:
    client = HevyAPIClient()

    if args.command == "fields":
        return _print_json({"body_measurement_fields": list(HevyAPIClient.body_measurement_fields())})
    if args.command == "list":
        return _print_json(client.list_body_measurements(page=args.page, page_size=args.page_size))
    if args.command == "get":
        return _print_json(client.get_body_measurement(args.date))
    if args.command == "create":
        payload = _build_measurement_payload(args, include_date=True)
        return _print_json(client.create_body_measurement(payload))
    if args.command == "update":
        payload = _build_measurement_payload(args, include_date=False)
        return _print_json(
            client.update_body_measurement(
                args.date,
                payload,
                preserve_existing=not args.replace,
            )
        )

    raise ValueError(f"Unsupported measurements command: {args.command}")


def _normalize_workout_title(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.casefold())
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", ascii_text).strip()


def _is_allowed_main_workout_title(title: str) -> bool:
    normalized = _normalize_workout_title(title)

    # Only include planned main split workouts labeled Day/Dia 1-6.
    day_match = re.search(r"\b(?:day|dia)\s*([1-6])\b", normalized)
    if not day_match:
        return False

    excluded_tokens = (
        "core",
        "abs",
        "abdominal",
        "forearm",
        "forearms",
        "antebrazo",
        "antebrazos",
        "calf",
        "calves",
        "pantorrilla",
        "pantorrillas",
        "gemelo",
        "gemelos",
    )
    return not any(token in normalized for token in excluded_tokens)


def _round_to_half(value: float) -> float:
    """Round value to nearest 0.5 increment (e.g., 7.5, 8, 8.5, 9, 9.5, 10)."""
    return round(value * 2) / 2


def _round_to_half(value: float) -> float:
    """Round value to nearest 0.5 increment (e.g., 7.5, 8, 8.5, 9, 9.5, 10)."""
    return round(value * 2) / 2


def _extract_workout_rpes(workout: dict[str, Any], include_warmups: bool) -> list[float]:
    values: list[float] = []
    exercises = workout.get("exercises", [])
    if not isinstance(exercises, list):
        return values

    for exercise in exercises:
        if not isinstance(exercise, dict):
            continue
        sets = exercise.get("sets", [])
        if not isinstance(sets, list):
            continue

        for set_data in sets:
            if not isinstance(set_data, dict):
                continue
            if not include_warmups and str(set_data.get("type", "")).casefold() == "warmup":
                continue
            rpe_value = set_data.get("rpe")
            if isinstance(rpe_value, (int, float)):
                values.append(float(rpe_value))

    return values


def _detect_workout_prs(client: HevyAPIClient, workout: dict[str, Any]) -> list[dict[str, Any]]:
    """Detect volume personal records in a workout by comparing against all prior exercise history.

    Returns one entry per exercise where at least one working set beat the previous volume PR.
    Within-session PRs (set A then set B both beating prior best) are collapsed to the best set.
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


def _find_latest_allowed_workouts(client: HevyAPIClient, max_count: int = 5, page_size: int = 10, max_pages: int = 30) -> list[dict[str, Any]]:
    """Find up to max_count latest allowed workouts."""
    results: list[dict[str, Any]] = []
    for page in range(1, max_pages + 1):
        payload = client.list_workouts(page=page, page_size=page_size)
        workouts = payload.get("workouts", [])
        if not isinstance(workouts, list) or not workouts:
            break

        for workout in workouts:
            if not isinstance(workout, dict):
                continue
            title = str(workout.get("title", ""))
            if _is_allowed_main_workout_title(title):
                results.append(workout)
                if len(results) >= max_count:
                    return results

        if len(workouts) < page_size:
            break

    return results


def _handle_workouts_command(args: argparse.Namespace) -> int:
    client = HevyAPIClient()

    if args.command == "latest-rpe":
        workouts_list = _find_latest_allowed_workouts(client, max_count=6)
        if not workouts_list:
            print("No qualifying workout found with title Day/Dia 1-6 excluding core/forearms/calves.")
            return 1

        nth = args.nth - 1  # Convert to 0-indexed
        if nth >= len(workouts_list):
            print(f"Only {len(workouts_list)} qualifying workouts available (requested nth={args.nth})")
            return 1

        workout = workouts_list[nth]
        if not workout.get("exercises"):
            workout_id = str(workout.get("id", ""))
            if workout_id:
                workout = client.get_workout(workout_id)

        all_set_rpes = _extract_workout_rpes(workout, include_warmups=True)
        work_set_rpes = _extract_workout_rpes(workout, include_warmups=False)

        result: dict[str, Any] = {
            "workout_id": workout.get("id"),
            "title": workout.get("title"),
            "start_time": workout.get("start_time"),
            "end_time": workout.get("end_time"),
            "nth_latest": args.nth,
            "filters": {
                "title_day_range": "Day/Dia 1-6",
                "excluded_keywords": ["core", "forearms", "calves"],
            },
            "set_count_with_rpe_all": len(all_set_rpes),
            "set_count_with_rpe_working": len(work_set_rpes),
            "overall_rpe": _round_to_half(mean(work_set_rpes)) if work_set_rpes else None,
        }
        if getattr(args, "show_prs", False):
            prs = _detect_workout_prs(client, workout)
            result["pr_count"] = len(prs)
            result["personal_records"] = prs
        return _print_json(result)

    if args.command == "last-rpes":
        workouts_list = _find_latest_allowed_workouts(client, max_count=6)
        if not workouts_list:
            print("No qualifying workouts found with title Day/Dia 1-6 excluding core/forearms/calves.")
            return 1

        results = []
        for idx, workout in enumerate(workouts_list):
            if not workout.get("exercises"):
                workout_id = str(workout.get("id", ""))
                if workout_id:
                    workout = client.get_workout(workout_id)

            work_set_rpes = _extract_workout_rpes(workout, include_warmups=False)
            entry: dict[str, Any] = {
                "nth_latest": idx + 1,
                "title": workout.get("title"),
                "start_time": workout.get("start_time"),
                "overall_rpe": _round_to_half(mean(work_set_rpes)) if work_set_rpes else None,
            }
            if getattr(args, "show_prs", False):
                prs = _detect_workout_prs(client, workout)
                entry["pr_count"] = len(prs)
                entry["personal_records"] = prs
            results.append(entry)

        return _print_json(results)

    if args.command == "personal-records":
        workouts_list = _find_latest_allowed_workouts(client, max_count=6)
        if not workouts_list:
            print("No qualifying workouts found with title Day/Dia 1-6 excluding core/forearms/calves.")
            return 1

        # Collect unique exercises from one full round of Day 1-6 workouts
        exercise_meta: dict[str, str] = {}  # ex_id -> title
        for w_meta in workouts_list:
            full = client.get_workout(str(w_meta.get("id", "")))
            for ex in full.get("exercises", []):
                ex_id = str(ex.get("exercise_template_id", ""))
                if ex_id and ex_id not in exercise_meta:
                    exercise_meta[ex_id] = str(ex.get("title", ""))

        records: list[dict[str, Any]] = []
        for ex_id, ex_title in exercise_meta.items():
            history = client.get_exercise_history(ex_id)
            working_sets = [
                s for s in history.get("exercise_history", [])
                if s.get("set_type") != "warmup"
            ]
            if not working_sets:
                continue

            best = max(
                working_sets,
                key=lambda s: float(s.get("weight_kg") or 0) * int(s.get("reps") or 0),
            )
            best_vol = float(best.get("weight_kg") or 0) * int(best.get("reps") or 0)
            records.append({
                "exercise": ex_title,
                "best_weight_kg": round(float(best.get("weight_kg") or 0), 2),
                "best_reps": int(best.get("reps") or 0),
                "best_volume": round(best_vol, 1),
                "achieved_on": str(best.get("workout_start_time", ""))[:10],
            })

        records.sort(key=lambda x: x["exercise"])
        return _print_json(records)

    raise ValueError(f"Unsupported workouts command: {args.command}")


def _list_input_routines(input_dir: str = "input") -> int:
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"Input directory not found: {input_dir}")
        return 1

    routine_files = sorted(input_path.glob("*.json"))
    if not routine_files:
        print(f"No routine JSON files found in {input_dir}")
        return 1

    print(f"Routine files in {input_dir}:")
    for routine_file in routine_files:
        print(f"- {routine_file.as_posix()}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Hevy Training Toolkit CLI",
        epilog=(
            "Examples:\n"
            "  python hevy_cli.py routines upload input/dia_1_pecho_hsf16.json --dry-run\n"
            "  python hevy_cli.py routines batch-upload extracted_routines.json --folder-title \"HSF 16\"\n"
            "  python hevy_cli.py folders recent\n"
            "  python hevy_cli.py folders create-next\n"
            "  python hevy_cli.py workouts latest-rpe"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="domain")

    routines_parser = subparsers.add_parser("routines", help="Routine upload and validation workflows")
    routines_subparsers = routines_parser.add_subparsers(dest="command")

    upload_parser = routines_subparsers.add_parser("upload", help="Delegate to routine_uploader.py")
    upload_parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments passed through to routine_uploader.py")

    batch_upload_parser = routines_subparsers.add_parser("batch-upload", help="Delegate to batch_routine_uploader.py")
    batch_upload_parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments passed through to batch_routine_uploader.py")

    validate_parser = routines_subparsers.add_parser("validate", help="Delegate to exercise_validator.py")
    validate_parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments passed through to exercise_validator.py")

    interactive_validate_parser = routines_subparsers.add_parser("interactive-validate", help="Validate and prompt for missing exercises")
    interactive_validate_parser.add_argument("routine_file", help="Routine JSON file to validate")
    interactive_validate_parser.add_argument("args", nargs=argparse.REMAINDER, help="Additional arguments passed through to exercise_validator.py")

    check_parser = routines_subparsers.add_parser("check", help="Delegate to validate_structure.py")
    check_parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments passed through to validate_structure.py")

    list_parser = routines_subparsers.add_parser("list-input", help="List routine JSON files in the input directory")
    list_parser.add_argument("input_dir", nargs="?", default="input", help="Directory to inspect (default: input)")

    summary_table_parser = routines_subparsers.add_parser(
        "summary-table",
        help="Print the required 4-column validation table from a routine JSON file",
    )
    summary_table_parser.add_argument("routine_file", help="Routine JSON file to summarize")
    summary_table_parser.add_argument(
        "--mappings",
        "--instructions",
        dest="mappings_file",
        default="exercise_mappings.md",
        help="Path to exercise_mappings.md for exercise name mapping (default: exercise_mappings.md)",
    )

    folders_parser = subparsers.add_parser("folders", help="Routine folder utilities")
    folders_subparsers = folders_parser.add_subparsers(dest="command")

    folders_subparsers.add_parser("recent", help="Show recent folders")
    folders_subparsers.add_parser("create-next", help="Create the next auto-incremented folder")

    create_parser = folders_subparsers.add_parser("create", help="Create a folder with a custom name")
    create_parser.add_argument("name", help="Folder name")

    folders_subparsers.add_parser("list", help="List routine folders")

    measurements_parser = subparsers.add_parser("measurements", help="Body measurement workflows")
    measurements_subparsers = measurements_parser.add_subparsers(dest="command")

    measurements_fields_parser = measurements_subparsers.add_parser("fields", help="List supported body measurement fields")

    measurements_list_parser = measurements_subparsers.add_parser("list", help="List body measurements")
    measurements_list_parser.add_argument("--page", type=int, default=1, help="Page number (default: 1)")
    measurements_list_parser.add_argument("--page-size", type=int, default=10, help="Page size, max 10 (default: 10)")

    measurements_get_parser = measurements_subparsers.add_parser("get", help="Get a body measurement by date")
    measurements_get_parser.add_argument("date", help="Measurement date in YYYY-MM-DD format")

    measurements_create_parser = measurements_subparsers.add_parser("create", help="Create a body measurement entry")
    measurements_create_parser.add_argument("--date", required=True, help="Measurement date in YYYY-MM-DD format")
    measurements_create_parser.add_argument("--json-file", help="Optional JSON file with a measurement payload")
    _add_measurement_field_arguments(measurements_create_parser)

    measurements_update_parser = measurements_subparsers.add_parser("update", help="Update a body measurement entry")
    measurements_update_parser.add_argument("date", help="Measurement date in YYYY-MM-DD format")
    measurements_update_parser.add_argument("--json-file", help="Optional JSON file with a measurement payload")
    measurements_update_parser.add_argument(
        "--replace",
        action="store_true",
        help="Send only the provided fields and let omitted fields become null",
    )
    _add_measurement_field_arguments(measurements_update_parser)

    workouts_parser = subparsers.add_parser("workouts", help="Workout history and analysis")
    workouts_subparsers = workouts_parser.add_subparsers(dest="command")

    latest_rpe_parser = workouts_subparsers.add_parser(
        "latest-rpe",
        help="Get overall RPE from latest qualifying Day/Dia 1-6 workout (excluding core/forearms/calves)",
    )
    latest_rpe_parser.add_argument(
        "--nth",
        type=int,
        default=1,
        choices=[1, 2, 3, 4, 5, 6],
        help="Select which of the latest 6 qualifying workouts to retrieve (1=latest, 6=oldest) (default: 1)",
    )
    latest_rpe_parser.add_argument(
        "--show-prs",
        action="store_true",
        help="Also detect and show personal records achieved in the workout",
    )

    last_rpes_parser = workouts_subparsers.add_parser(
        "last-rpes",
        help="Get overall RPE for the last 6 qualifying Day/Dia 1-6 workouts (excluding core/forearms/calves)",
    )
    last_rpes_parser.add_argument(
        "--show-prs",
        action="store_true",
        help="Also detect and show personal records achieved in each workout",
    )

    workouts_subparsers.add_parser(
        "personal-records",
        help="Show all-time volume PRs for every exercise in the last full round of Day 1-6 workouts",
    )

    auth_parser = subparsers.add_parser("auth", help="Verify Hevy API authentication")
    auth_parser.add_argument("api_key", nargs="?", help="Optional API key override")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.domain == "routines":
        if args.command == "upload":
            return _run_entrypoint(routine_uploader.main, ["routine_uploader.py", *args.args])
        if args.command == "batch-upload":
            return _run_entrypoint(batch_routine_uploader.main, ["batch_routine_uploader.py", *args.args])
        if args.command == "validate":
            return _run_entrypoint(exercise_validator.main, ["exercise_validator.py", *args.args])
        if args.command == "interactive-validate":
            return _run_entrypoint(
                exercise_validator.main,
                ["exercise_validator.py", args.routine_file, "--interactive", *args.args],
            )
        if args.command == "check":
            return _run_entrypoint(validate_structure.main, ["validate_structure.py", *args.args])
        if args.command == "list-input":
            return _list_input_routines(args.input_dir)
        if args.command == "summary-table":
            return _print_routine_summary_table(args.routine_file, args.mappings_file)
        routines_parser = next(action for action in parser._actions if isinstance(action, argparse._SubParsersAction))
        routines_parser.choices["routines"].print_help()
        return 1

    if args.domain == "folders":
        if args.command == "recent":
            return 0 if get_recent_folder.main() else 1
        if args.command == "create-next":
            return 0 if create_new_folder.main() else 1
        if args.command == "create":
            return _run_entrypoint(folder_manager.main, ["folder_manager.py", "create", args.name])
        if args.command == "list":
            return _run_entrypoint(folder_manager.main, ["folder_manager.py", "list"])
        folders_parser = next(action for action in parser._actions if isinstance(action, argparse._SubParsersAction))
        folders_parser.choices["folders"].print_help()
        return 1

    if args.domain == "measurements":
        if not args.command:
            measurements_parser = next(action for action in parser._actions if isinstance(action, argparse._SubParsersAction))
            measurements_parser.choices["measurements"].print_help()
            return 1
        return _handle_measurements_command(args)

    if args.domain == "workouts":
        if not args.command:
            workouts_parser = next(action for action in parser._actions if isinstance(action, argparse._SubParsersAction))
            workouts_parser.choices["workouts"].print_help()
            return 1
        return _handle_workouts_command(args)

    if args.domain == "auth":
        auth_argv = ["test_api_key.py"]
        if args.api_key:
            auth_argv.append(args.api_key)
        return _run_entrypoint(test_api_key.main, auth_argv)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())