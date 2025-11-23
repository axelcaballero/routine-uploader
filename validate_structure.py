#!/usr/bin/env python3
"""
Pre-upload validator for Hevy routine JSON files
Catches structural errors BEFORE sending to API
"""

import json
import sys
from pathlib import Path


def validate_routine_structure(file_path):
    """Validate routine JSON structure against known API requirements"""
    
    errors = []
    warnings = []
    
    # Load JSON
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"❌ Invalid JSON: {e}"], []
    except FileNotFoundError:
        return [f"❌ File not found: {file_path}"], []
    
    # Check 1: Root "routine" key
    if "routine" not in data:
        errors.append("❌ Missing root 'routine' key - should be: { \"routine\": { ... } }")
    else:
        routine = data["routine"]
        
        # Check 2: Required routine fields
        if "title" not in routine:
            errors.append("❌ Missing routine.title")
        if "folder_id" not in routine:
            errors.append("❌ Missing routine.folder_id (should be 1812915)")
        elif routine["folder_id"] != 1812915:
            warnings.append(f"⚠️  Unusual folder_id: {routine['folder_id']} (typically 1812915)")
        
        if "exercises" not in routine:
            errors.append("❌ Missing routine.exercises array")
        else:
            exercises = routine["exercises"]
            
            if not isinstance(exercises, list):
                errors.append("❌ routine.exercises should be an array []")
            else:
                # Check 3: Each exercise structure
                for i, exc in enumerate(exercises):
                    exc_num = i + 1
                    
                    # Required fields
                    if "exercise_template_id" not in exc:
                        errors.append(f"❌ Exercise #{exc_num}: missing exercise_template_id")
                    
                    if "sets" not in exc:
                        errors.append(f"❌ Exercise #{exc_num}: missing sets array")
                    elif not isinstance(exc["sets"], list):
                        errors.append(f"❌ Exercise #{exc_num}: sets should be an array []")
                    else:
                        # Check 4: Set types (CRITICAL)
                        for j, set_item in enumerate(exc["sets"]):
                            set_num = j + 1
                            
                            if "type" not in set_item:
                                errors.append(f"❌ Exercise #{exc_num}, Set #{set_num}: missing 'type' field")
                            else:
                                set_type = set_item["type"]
                                # Valid types per Hevy API documentation: https://api.hevyapp.com/docs/#/
                                valid_types = ["warmup", "normal", "dropset", "failure"]
                                if set_type not in valid_types:
                                    errors.append(
                                        f"❌ Exercise #{exc_num}, Set #{set_num}: "
                                        f"type='{set_type}' is INVALID (must be one of: {', '.join(valid_types)})"
                                    )
                            
                            # Check for weight/reps/duration consistency
                            weight_kg = set_item.get("weight_kg") or 0
                            reps = set_item.get("reps") or 0
                            duration_sec = set_item.get("duration_seconds") or 0
                            
                            if duration_sec > 0 and (weight_kg > 0 or reps > 0):
                                warnings.append(
                                    f"⚠️  Exercise #{exc_num}, Set #{set_num}: "
                                    f"Has both duration ({duration_sec}sec) AND weight/reps - typically use one or other"
                                )
                    
                    # Optional but check superset_id
                    if "superset_id" in exc and exc["superset_id"] is not None:
                        warnings.append(f"⚠️  Exercise #{exc_num}: superset_id is set (we don't use supersets)")
    
    return errors, warnings


def print_results(file_path, errors, warnings):
    """Print validation results in readable format"""
    
    filename = Path(file_path).name
    print(f"\n{'='*60}")
    print(f"📋 Validating: {filename}")
    print(f"{'='*60}\n")
    
    if errors:
        print("❌ CRITICAL ERRORS (will cause API failure):")
        for error in errors:
            print(f"   {error}")
        print()
    
    if warnings:
        print("⚠️  WARNINGS (non-blocking):")
        for warning in warnings:
            print(f"   {warning}")
        print()
    
    if not errors and not warnings:
        print("✅ All checks passed! Structure is valid.")
        print("   Ready for: ./routines.sh validate <file>")
        print()
        return True
    elif not errors:
        print("✅ Structure is valid (warnings only). Safe to upload.")
        print()
        return True
    else:
        print("❌ Fix errors above before uploading.")
        print(f"\n   Quick fix: Review API_STRUCTURE_GUIDE.md")
        print()
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate_structure.py <routine.json>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    errors, warnings = validate_routine_structure(file_path)
    success = print_results(file_path, errors, warnings)
    
    sys.exit(0 if success or not errors else 1)


if __name__ == "__main__":
    main()
