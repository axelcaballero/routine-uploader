#!/usr/bin/env python3
"""Umbrella CLI for Hevy training workflows."""

from __future__ import annotations

import argparse
import json
import re
import sys
from contextlib import contextmanager
from pathlib import Path
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


def _load_exercise_name_index(instructions_path: str = "instructions.md") -> dict[str, tuple[str, str]]:
    """Build exercise ID -> (source exercise name, Hevy exercise name) index from instructions.md."""
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

    normal_reps = [
        int(series.get("reps"))
        for series in sets
        if isinstance(series, dict)
        and series.get("type") == "normal"
        and isinstance(series.get("reps"), int)
    ]

    if not normal_reps:
        return "-"

    notes = str(exercise.get("notes", "")).lower()
    is_cluster = "cluster" in notes
    if is_cluster:
        return f"cluster: {_collapse_reps_for_cluster(normal_reps)}"

    if len(set(normal_reps)) == 1:
        return f"{len(normal_reps)}x{normal_reps[0]}"

    return " + ".join(f"1x{rep}" for rep in normal_reps)


def _print_routine_summary_table(routine_file: str, instructions_path: str = "instructions.md") -> int:
    payload = _load_json_payload(routine_file)
    routine = payload.get("routine")
    if not isinstance(routine, dict):
        raise ValueError(f"Invalid routine JSON: missing 'routine' object in {routine_file}")

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
            "  python hevy_cli.py folders create-next"
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
        "--instructions",
        default="instructions.md",
        help="Path to instructions.md for exercise name mapping (default: instructions.md)",
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

    subparsers.add_parser("workouts", help="Reserved umbrella namespace for workout history and analysis")
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
            return _print_routine_summary_table(args.routine_file, args.instructions)
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
        return _print_planned_capability("Workout")

    if args.domain == "auth":
        auth_argv = ["test_api_key.py"]
        if args.api_key:
            auth_argv.append(args.api_key)
        return _run_entrypoint(test_api_key.main, auth_argv)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())