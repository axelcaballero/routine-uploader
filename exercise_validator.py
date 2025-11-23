#!/Users/axelcaballero/projects/hevy/routine-uploader/venv/bin/python
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
        """
        exercise_map = {}
        
        try:
            with open(self.instructions_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            current_category = None
            current_exercise = None
            
            for line in lines:
                line = line.strip()
                
                # Detect category headers
                if re.match(r'^##+ \w+', line):
                    current_category = re.sub(r'^##+ ', '', line)
                    if current_category:
                        exercise_map[current_category] = {}
                    continue
                
                # Detect exercise entries starting with *
                if line.startswith('*'):
                    # Extract exercise name and possible ID from this line
                    match = re.match(r'\*\s+(.+)', line)
                    if match:
                        content = match.group(1)
                        
                        # Check for pipe-delimited format: Spanish name | ID | NOTES
                        if '|' in content:
                            parts = content.split('|')
                            if len(parts) >= 2:
                                exercise_part = parts[0].strip()
                                id_part = parts[1].strip()
                                # Remove parentheses and check if it's a valid ID
                                template_id = id_part.replace('(', '').replace(')', '').strip()
                                
                                # Extract exercise name (Spanish part before "es")
                                exercise_name = re.sub(r'\s+(?:es|equivale)\s+.+$', '', exercise_part, flags=re.IGNORECASE)
                                exercise_name = exercise_name.strip()
                                
                                if current_category and exercise_name and len(template_id) >= 8:
                                    exercise_map[current_category][exercise_name] = template_id
                                current_exercise = None
                        else:
                            # Fallback to old format without pipes (for backward compatibility)
                            # Look for an ID (hex or UUID) anywhere in the line
                            id_match = re.search(r'([A-Fa-f0-9]{8}(?:[A-Fa-f0-9]{4}|\-[A-Fa-f0-9]{4})*(?:\-[A-Fa-f0-9]{12})?)\)?\s*(?:\.|$)', content)
                            
                            if id_match:
                                # Full exercise line with ID
                                template_id = id_match.group(1).strip()
                                # Remove the ID from content to get exercise name
                                exercise_name = content[:id_match.start()].strip()
                                # Remove English descriptions (after "es", "equivale", etc.)
                                exercise_name = re.sub(r'\s+(?:es|equivale)\s+.+$', '', exercise_name, flags=re.IGNORECASE)
                                exercise_name = exercise_name.strip()
                                
                                if current_category and exercise_name and len(template_id) >= 8:
                                    exercise_map[current_category][exercise_name] = template_id
                                current_exercise = None
                            else:
                                # Exercise without ID (might be continued on next line)
                                current_exercise = (content, current_category)
                
                # Handle wrapped IDs (ID on next line)
                elif current_exercise:
                    id_match = re.search(r'^([A-Fa-f0-9]{8}(?:[A-Fa-f0-9]{4}|\-[A-Fa-f0-9]{4})*(?:\-[A-Fa-f0-9]{12})?)', line)
                    if id_match:
                        template_id = id_match.group(1).strip()
                        exercise_name = current_exercise[0]
                        category = current_exercise[1]
                        # Remove English descriptions
                        exercise_name = re.sub(r'\s+(?:es|equivale)\s+.+$', '', exercise_name, flags=re.IGNORECASE)
                        exercise_name = exercise_name.strip()
                        
                        if category and exercise_name and len(template_id) >= 8:
                            exercise_map[category][exercise_name] = template_id
                        current_exercise = None
            
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
    
    def validate_routine(self, routine_data: Dict, verbose: bool = False, interactive: bool = False) -> Tuple[bool, List[str]]:
        """
        Validate all exercises in a routine against instructions.md.
        
        Args:
            routine_data: Routine JSON data
            verbose: If True, print detailed information
            interactive: If True, prompt user for missing exercises
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        missing_exercises = []  # Track exercises not found
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
                # Store missing exercise info for interactive mode
                missing_exercises.append({
                    'index': i,
                    'ex_id': ex_id,
                    'notes': notes,
                    'exercise_data': exercise
                })
            
            if verbose or status == "⚠":
                print(f"   {status} {message}")
        
        is_valid = len(errors) == 0
        
        if is_valid:
            print("\n✅ All exercise IDs are valid!")
        else:
            print(f"\n❌ Found {len(errors)} validation error(s)!")
            
            # In interactive mode, ask user about missing exercises
            if interactive and missing_exercises:
                print("\n📝 Processing missing exercises...")
                for missing in missing_exercises:
                    self._handle_missing_exercise(missing)
        
        return is_valid, errors
    
    def _handle_missing_exercise(self, missing_info: Dict) -> None:
        """
        Interactively handle a missing exercise by asking user for details
        and adding it to instructions.md
        
        Args:
            missing_info: Dict with exercise_template_id, notes, and index
        """
        print(f"\n❓ Exercise #{missing_info['index']} not found: {missing_info['ex_id']}")
        print(f"   Notes: {missing_info['notes']}")
        
        # Ask for exercise details
        exercise_name = input("   Enter Spanish exercise name: ").strip()
        if not exercise_name:
            print("   ⏭️  Skipping this exercise")
            return
        
        category = input("   Enter category (Pecho/Hombro/Espalda/Biceps/Triceps/Pierna/Core): ").strip()
        if not category:
            print("   ⏭️  Skipping this exercise")
            return
        
        english_name = input("   Enter English exercise name (optional): ").strip()
        
        # Add to instructions.md
        self._add_exercise_to_instructions(exercise_name, english_name, missing_info['ex_id'], category)
        
        # Reload the exercise map
        self.exercise_map = self._parse_instructions()
        print(f"   ✅ Added '{exercise_name}' to instructions.md in category '{category}'")
    
    def _add_exercise_to_instructions(self, spanish_name: str, english_name: str, template_id: str, category: str) -> None:
        """
        Add a new exercise entry to instructions.md
        
        Args:
            spanish_name: Spanish name of the exercise
            english_name: English name/description of the exercise
            template_id: Hevy template ID
            category: Exercise category
        """
        try:
            with open(self.instructions_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find the category section
            category_pattern = f"^## {category}\n"
            if not re.search(category_pattern, content, re.MULTILINE):
                print(f"   ⚠️  Category '{category}' not found in instructions.md")
                return
            
            # Create the new entry in pipe-delimited format
            if english_name:
                new_entry = f"* {spanish_name} es {english_name} | {template_id}\n"
            else:
                new_entry = f"* {spanish_name} | {template_id}\n"
            
            # Find where to insert (before the next category header or at end of section)
            insert_pattern = f"(^## {category}\n(?:.*?\n)*?)(^## |\\Z)"
            
            def replacer(match):
                section = match.group(1)
                next_part = match.group(2)
                # Insert before the last newline if section ends with newline
                if section.endswith('\n'):
                    return section + new_entry + next_part
                return section + '\n' + new_entry + next_part
            
            new_content = re.sub(insert_pattern, replacer, content, flags=re.MULTILINE)
            
            # Write back
            with open(self.instructions_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
        except Exception as e:
            print(f"   ❌ Error adding exercise to instructions.md: {e}")

    
    def validate_from_file(self, routine_path: str, verbose: bool = False, interactive: bool = False) -> Tuple[bool, List[str]]:
        """
        Validate a routine JSON file.
        
        Args:
            routine_path: Path to routine JSON file
            verbose: If True, print detailed information
            interactive: If True, prompt user for missing exercises
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        try:
            with open(routine_path, 'r', encoding='utf-8') as f:
                routine_data = json.load(f)
            
            routine_title = routine_data.get('routine', {}).get('title', 'Unknown')
            print(f"📋 Validating: {routine_title}")
            
            return self.validate_routine(routine_data, verbose=verbose, interactive=interactive)
        
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
        "-inst", "--instructions",
        default="instructions.md",
        help="Path to instructions.md (default: instructions.md)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print detailed validation information"
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Prompt for missing exercises and add them to instructions.md"
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
    
    is_valid, errors = validator.validate_from_file(args.routine_file, verbose=args.verbose, interactive=args.interactive)
    
    if not is_valid:
        print("\n❌ Validation failed! Please correct the exercise IDs.")
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
