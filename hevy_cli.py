#!/usr/bin/env python3
"""Umbrella CLI for Hevy training workflows."""

from __future__ import annotations

import argparse
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Iterator, Sequence

import batch_routine_uploader
import create_new_folder
import exercise_validator
import folder_manager
import get_recent_folder
import routine_uploader
import test_api_key
import validate_structure


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

    folders_parser = subparsers.add_parser("folders", help="Routine folder utilities")
    folders_subparsers = folders_parser.add_subparsers(dest="command")

    folders_subparsers.add_parser("recent", help="Show recent folders")
    folders_subparsers.add_parser("create-next", help="Create the next auto-incremented folder")

    create_parser = folders_subparsers.add_parser("create", help="Create a folder with a custom name")
    create_parser.add_argument("name", help="Folder name")

    folders_subparsers.add_parser("list", help="List routine folders")

    subparsers.add_parser("measurements", help="Reserved umbrella namespace for body measurements")
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
        return _print_planned_capability("Measurements")

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