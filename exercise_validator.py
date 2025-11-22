#!/usr/bin/env python3
"""
Exercise ID Validator
Validates exercise template IDs against the authoritative source (instructions.md)
to prevent mismatches when creating routines.
"""

import json
import re
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class ExerciseValidator:
    """Validates exercise IDs against instructions.md mappings"""
    
    def __init__(self, instructions_path: str = "instructions.md"):
        """
        Initialize validator with instructions file.
        
        Args:
            instructions_path: Path to instructions.md file
        """
        self.instructions_path = instructions_path
        self.exercise_map = self._parse_instructions()
    
    def _parse_instructions(self) -> Dict[str, Dict[str, str]]:
        """
        Parse instructions.md to extract exercise mappings.
        
        Returns:
            Dictionary mapping exercise names to their template IDs
            Format: {
                "category": {
                    "spanish_name": "template_id",
                    ...
                }
            }
        """
        exercise_map = {}
        
        try:
            with open(self.instructions_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split by category headers
            categories = re.split(r'^### ', content, flags=re.MULTILINE)[1:]
            
            for category_block in categories:
                lines = category_block.split('\n')
                category_name = lines[0].strip()
                exercise_map[category_name] = {}
                
                # Parse exercise lines
                for line in lines[1:]:
                    # Match pattern: * Spanish name equivale/es ... ID
                    match = re.search(
                        r'\* ([^*]+?)\s+(?:equivale|es)\s+(?:.*?\s)?([A-Fa-f0-9\-]{8,})\s*$',
                        line.strip()
                    )
                    
                    if match:
                        spanish_name = match.group(1).strip()
                        template_id = match.group(2).strip()
                        exercise_map[category_name][spanish_name] = template_id
            
            return exercise_map
        
        except FileNotFoundError:
            print(f"❌ Error: {self.instructions_path} not found")
            return {}
    
    def get_id_for_exercise(self, exercise_name: str) -> Optional[str]:
        """
        Get the template ID for a given exercise name.
        
        Args:
            exercise_name: Spanish name of the exercise (or partial name)
            
        Returns:
            Template ID or None if not found
        """
        # Search across all categories
        for category, exercises in self.exercise_map.items():
            for spanish_name, template_id in exercises.items():
                # Exact match
                if spanish_name.lower() == exercise_name.lower():
                    return template_id
                
                # Partial match (useful for variations)
                if exercise_name.lower() in spanish_name.lower():
                    return template_id
        
        return None
    
    def validate_routine(self, routine_data: Dict, verbose: bool = False) -> Tuple[bool, List[str]]:
        """
        Validate all exercises in a routine against instructions.md.
        
        Args:
            routine_data: Routine JSON data
            verbose: If True, print detailed information
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        exercises = routine_data.get('routine', {}).get('exercises', [])
        
        print(f"\n🔍 Validating {len(exercises)} exercises against instructions.md...\n")
        
        for i, exercise in enumerate(exercises, 1):
            ex_id = exercise.get('exercise_template_id')
            notes = exercise.get('notes', '')
            
            # Check if ID exists in our mapping
            found_in_map = False
            found_category = None
            found_name = None
            
            for category, exercises_dict in self.exercise_map.items():
                for spanish_name, template_id in exercises_dict.items():
                    if template_id == ex_id:
                        found_in_map = True
                        found_category = category
                        found_name = spanish_name
                        break
                if found_in_map:
                    break
            
            if found_in_map:
                status = "✓"
                message = f"{i}. {ex_id} → {found_name} ({found_category})"
            else:
                status = "⚠"
                message = f"{i}. {ex_id} - NOT FOUND IN instructions.md! Notes: {notes[:50]}"
                errors.append(message)
            
            if verbose or status == "⚠":
                print(f"   {status} {message}")
        
        is_valid = len(errors) == 0
        
        if is_valid:
            print("\n✅ All exercise IDs are valid!")
        else:
            print(f"\n❌ Found {len(errors)} validation error(s)!")
        
        return is_valid, errors
    
    def validate_from_file(self, routine_path: str, verbose: bool = False) -> Tuple[bool, List[str]]:
        """
        Validate a routine JSON file.
        
        Args:
            routine_path: Path to routine JSON file
            verbose: If True, print detailed information
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        try:
            with open(routine_path, 'r', encoding='utf-8') as f:
                routine_data = json.load(f)
            
            routine_title = routine_data.get('routine', {}).get('title', 'Unknown')
            print(f"📋 Validating: {routine_title}")
            
            return self.validate_routine(routine_data, verbose=verbose)
        
        except FileNotFoundError:
            error_msg = f"Routine file not found: {routine_path}"
            print(f"❌ {error_msg}")
            return False, [error_msg]
        except json.JSONDecodeError:
            error_msg = f"Invalid JSON in {routine_path}"
            print(f"❌ {error_msg}")
            return False, [error_msg]
    
    def print_available_exercises(self) -> None:
        """Print all available exercises from instructions.md"""
        print("\n📚 Available Exercises from instructions.md:\n")
        print("=" * 80)
        
        for category, exercises in sorted(self.exercise_map.items()):
            print(f"\n### {category}")
            for spanish_name, template_id in sorted(exercises.items()):
                print(f"  • {spanish_name}")
                print(f"    ID: {template_id}")
        
        print("\n" + "=" * 80)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validate routine exercise IDs against instructions.md"
    )
    parser.add_argument(
        "routine_file",
        nargs="?",
        help="Path to routine JSON file to validate"
    )
    parser.add_argument(
        "-i", "--instructions",
        default="instructions.md",
        help="Path to instructions.md (default: instructions.md)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print detailed validation information"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available exercises from instructions.md"
    )
    
    args = parser.parse_args()
    
    validator = ExerciseValidator(args.instructions)
    
    if args.list:
        validator.print_available_exercises()
        return
    
    if not args.routine_file:
        parser.print_help()
        return
    
    is_valid, errors = validator.validate_from_file(args.routine_file, verbose=args.verbose)
    
    if not is_valid:
        print("\n❌ Validation failed! Please correct the exercise IDs.")
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
