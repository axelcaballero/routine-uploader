"""
Validate Routine Compliance with ROUTINE_CREATION_RULES.md

This script validates routine JSON files against ALL rules before upload.
Run this BEFORE batch_routine_uploader.py to prevent violations.

Usage:
    python validate_rules_compliance.py input/dia_1_pecho_hombro_dic.json
    python validate_rules_compliance.py input/*.json  # Validate all
"""

import json
import sys
import re
from pathlib import Path

# Exercises that ALWAYS require doubled reps (Rule 3)
REQUIRES_DOUBLING = {
    # Hombro
    "0D2C58FA-D4A1-4C3F-BF38-7D39FF74E96F",  # Press militar con mancuerna
    "4BBC7F4C",  # Elevaciones laterales con mancuerna
    "E8F9C0D3",  # Elevaciones frontales con mancuerna
    "A5D92BE2",  # Elevaciones posteriores con mancuerna
    
    # Bíceps
    "724CDE60",  # Curl concentrado con mancuerna
    "37FCC2BB",  # Curl alternado con mancuerna
    "BFB6D1A4",  # Curl martillo con mancuerna
    "3F80FF21",  # Curl con mancuerna (supino)
    
    # Tríceps
    "93DD5E54",  # Extensión de tríceps por encima de la cabeza con mancuerna
    "03821A49",  # Extensiones de tríceps inclinado con mancuerna
    "F566A9A1",  # Patada de tríceps con mancuerna
}


class RuleViolation:
    """Container for rule violation details"""
    def __init__(self, rule_number, exercise_idx, description, severity="ERROR"):
        self.rule_number = rule_number
        self.exercise_idx = exercise_idx
        self.description = description
        self.severity = severity
    
    def __str__(self):
        emoji = "❌" if self.severity == "ERROR" else "⚠️ "
        return f"{emoji} Rule {self.rule_number} | Exercise {self.exercise_idx + 1}: {self.description}"


def validate_rule_1_rep_ranges(exercise, exercise_idx):
    """
    Rule 1: Rep ranges must use maximum value
    Example: "4x6-8rep" should have 8 reps, not 6
    """
    violations = []
    notes = exercise.get('notes', '')
    
    # Extract rep range from notes (e.g., "6-8rep", "12-15rep")
    rep_range_match = re.search(r'(\d+)-(\d+)\s*rep', notes)
    
    if rep_range_match:
        min_reps = int(rep_range_match.group(1))
        max_reps = int(rep_range_match.group(2))
        
        # Check if sets use max value
        sets = exercise.get('sets', [])
        for set_idx, set_obj in enumerate(sets):
            if set_obj.get('type') == 'normal':  # Skip warmup
                actual_reps = set_obj.get('reps', 0)
                
                # Account for doubling
                expected_reps = max_reps
                if exercise['exercise_template_id'] in REQUIRES_DOUBLING:
                    expected_reps *= 2
                
                if actual_reps != expected_reps and actual_reps != 0:
                    violations.append(RuleViolation(
                        1, exercise_idx,
                        f"Set {set_idx+1} has {actual_reps} reps, expected {expected_reps} (max from range {min_reps}-{max_reps})"
                    ))
    
    return violations


def validate_rule_3_doubling(exercise, exercise_idx):
    """
    Rule 3: 11 exercises ALWAYS require doubled reps
    """
    violations = []
    exercise_id = exercise.get('exercise_template_id', '')
    
    if exercise_id in REQUIRES_DOUBLING:
        sets = exercise.get('sets', [])
        notes = exercise.get('notes', '')
        
        # Extract expected reps from notes
        rep_match = re.search(r'(\d+)x(\d+)(?:-\d+)?rep', notes)
        if rep_match:
            base_reps = int(rep_match.group(2))
            expected_reps = base_reps * 2
            
            for set_idx, set_obj in enumerate(sets):
                if set_obj.get('type') in ['normal', 'warmup']:
                    actual_reps = set_obj.get('reps', 0)
                    
                    # Warmup should also be doubled (24 instead of 12)
                    if set_obj.get('type') == 'warmup':
                        expected = 24
                    else:
                        expected = expected_reps
                    
                    if actual_reps != expected and actual_reps != 0:
                        violations.append(RuleViolation(
                            3, exercise_idx,
                            f"Set {set_idx+1} has {actual_reps} reps, expected {expected} (doubling required)"
                        ))
    
    return violations


def validate_rule_4_warmup_sets(exercise, exercise_idx):
    """
    Rule 4: EVERY exercise must have warmup set as first set
    Warmup reps: 12 (or 24 if doubling required)
    """
    violations = []
    sets = exercise.get('sets', [])
    
    if not sets:
        violations.append(RuleViolation(
            4, exercise_idx,
            "No sets found - exercise must have at least a warmup set"
        ))
        return violations
    
    first_set = sets[0]
    
    # Check if first set is warmup
    if first_set.get('type') != 'warmup':
        violations.append(RuleViolation(
            4, exercise_idx,
            f"First set is type '{first_set.get('type')}', must be 'warmup'"
        ))
    
    # Check warmup reps (12 or 24)
    exercise_id = exercise.get('exercise_template_id', '')
    expected_warmup_reps = 24 if exercise_id in REQUIRES_DOUBLING else 12
    actual_warmup_reps = first_set.get('reps', 0)
    
    if actual_warmup_reps != expected_warmup_reps and actual_warmup_reps != 0:
        violations.append(RuleViolation(
            4, exercise_idx,
            f"Warmup set has {actual_warmup_reps} reps, expected {expected_warmup_reps}"
        ))
    
    return violations


def validate_rule_5_no_rpe(exercise, exercise_idx):
    """
    Rule 5: NO RPE field in routine exercises
    """
    violations = []
    
    if 'rpe' in exercise:
        violations.append(RuleViolation(
            5, exercise_idx,
            "RPE field found - this is ONLY for workout logs, NOT routines"
        ))
    
    # Check sets too
    for set_idx, set_obj in enumerate(exercise.get('sets', [])):
        if 'rpe' in set_obj:
            violations.append(RuleViolation(
                5, exercise_idx,
                f"Set {set_idx+1} has RPE field - NOT allowed in routines"
            ))
    
    return violations


def validate_rule_6_rest_times(exercise, exercise_idx, is_core_routine):
    """
    Rule 6: Correct rest_seconds values
    - Default: 60 seconds
    - Supersets: 0 for all except last (120)
    - Core: 20 seconds
    - Special cases: 30 or 20 based on notes
    """
    violations = []
    rest_seconds = exercise.get('rest_seconds', 60)
    notes = exercise.get('notes', '').lower()
    superset_id = exercise.get('superset_id')
    
    # Determine expected rest time
    if is_core_routine:
        expected_rest = 20
    elif '10-20seg' in notes:
        expected_rest = 20
    elif 'bulgaro' in notes or 'búlgaro' in notes:
        if '10-30seg' in notes:
            expected_rest = 30
        else:
            expected_rest = 60
    elif superset_id:
        # Can't validate without knowing if it's last in superset
        # Just warn if it's not 0 or 120
        if rest_seconds not in [0, 120]:
            violations.append(RuleViolation(
                6, exercise_idx,
                f"Superset exercise has {rest_seconds}s rest - should be 0 (not last) or 120 (last)",
                severity="WARNING"
            ))
        return violations
    else:
        expected_rest = 60
    
    if rest_seconds != expected_rest:
        violations.append(RuleViolation(
            6, exercise_idx,
            f"Has {rest_seconds}s rest, expected {expected_rest}s"
        ))
    
    return violations


def validate_rule_9_set_types(exercise, exercise_idx):
    """
    Rule 9: Set types must be valid
    Allowed: "normal", "warmup", "failure", "dropset"
    """
    violations = []
    valid_types = {"normal", "warmup", "failure", "dropset"}
    
    for set_idx, set_obj in enumerate(exercise.get('sets', [])):
        set_type = set_obj.get('type', '')
        if set_type not in valid_types:
            violations.append(RuleViolation(
                9, exercise_idx,
                f"Set {set_idx+1} has invalid type '{set_type}' - must be one of: {', '.join(valid_types)}"
            ))
    
    return violations


def validate_routine(file_path):
    """
    Validate a single routine JSON file against all rules
    """
    print(f"\n{'='*70}")
    print(f"📋 Validating: {file_path.name}")
    print(f"{'='*70}")
    
    # Load routine
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load JSON: {e}")
        return False
    
    routine = data.get('routine', {})
    title = routine.get('title', 'Unknown')
    exercises = routine.get('exercises', [])
    
    print(f"📝 Title: {title}")
    print(f"🏋️  Exercises: {len(exercises)}")
    
    is_core_routine = 'core' in title.lower()
    if is_core_routine:
        print("🎯 Core routine detected")
    
    # Collect all violations
    all_violations = []
    
    for idx, exercise in enumerate(exercises):
        # Run all validation rules
        all_violations.extend(validate_rule_1_rep_ranges(exercise, idx))
        all_violations.extend(validate_rule_3_doubling(exercise, idx))
        all_violations.extend(validate_rule_4_warmup_sets(exercise, idx))
        all_violations.extend(validate_rule_5_no_rpe(exercise, idx))
        all_violations.extend(validate_rule_6_rest_times(exercise, idx, is_core_routine))
        all_violations.extend(validate_rule_9_set_types(exercise, idx))
    
    # Report results
    errors = [v for v in all_violations if v.severity == "ERROR"]
    warnings = [v for v in all_violations if v.severity == "WARNING"]
    
    if not all_violations:
        print("✅ All validation checks passed!")
        return True
    
    if errors:
        print(f"\n❌ Found {len(errors)} error(s):")
        for violation in errors:
            print(f"  {violation}")
    
    if warnings:
        print(f"\n⚠️  Found {len(warnings)} warning(s):")
        for violation in warnings:
            print(f"  {violation}")
    
    return len(errors) == 0


def main():
    """
    Validate all provided routine files
    """
    if len(sys.argv) < 2:
        print("Usage: python validate_rules_compliance.py <file1.json> [file2.json ...]")
        print("Example: python validate_rules_compliance.py input/dia_*.json")
        sys.exit(1)
    
    files = [Path(arg) for arg in sys.argv[1:] if arg.endswith('.json')]
    
    if not files:
        print("❌ No JSON files provided")
        sys.exit(1)
    
    print("🚀 Starting Routine Rules Validation")
    print(f"📁 Files to validate: {len(files)}")
    
    results = {
        'passed': 0,
        'failed': 0
    }
    
    for file_path in files:
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            results['failed'] += 1
            continue
        
        passed = validate_routine(file_path)
        
        if passed:
            results['passed'] += 1
        else:
            results['failed'] += 1
    
    # Summary
    print("\n" + "="*70)
    print("📊 VALIDATION SUMMARY")
    print("="*70)
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"📝 Total: {len(files)}")
    print("="*70)
    
    if results['failed'] == 0:
        print("🎉 All routines passed validation! Safe to upload.")
        sys.exit(0)
    else:
        print("⚠️  Some routines failed validation. Fix errors before uploading!")
        sys.exit(1)


if __name__ == "__main__":
    main()
