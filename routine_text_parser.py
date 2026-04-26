#!/Users/axelcaballero/projects/hevy/routine-uploader/venv/bin/python
"""
Routine Text Parser - Converts plain text routine descriptions to JSON format.

Parses text files from routine-extractor into validated JSON for batch upload.
"""

import json
import sys
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple


class RoutineTextParser:
    """Parses plain text routine descriptions into JSON format."""
    ROUTINE_TITLE_PATTERN = re.compile(r'^(dia|día|day)\s*(\d+)\s*[-–:]?\s*(.*)$', re.IGNORECASE)
    
    def __init__(self, exercise_mappings_file: str = "instructions.md"):
        self.exercise_mappings = self._load_exercise_mappings(exercise_mappings_file)
        self.folder_id = 1812915
        self.core_keywords = [
            'core', 'plancha', 'plank', 'crunch', 'abdominal', 'abs',
            'oblicuo', 'oblique', 'mountain climber', 'vacio abdominal',
            'v up', 'v-up', 'toe touch', 'side plank', 'bicycle crunch',
            'reverse crunch', 'leg raise', 'elbow to knee'
        ]
        self.muscle_group_keywords = [
            'pecho', 'espalda', 'hombro', 'pierna', 'biceps', 'triceps',
            'chest', 'back', 'shoulder', 'leg', 'arms', 'push', 'pull'
        ]
        self.routine_title_keyword_map = {
            'pecho': 'Chest',
            'espalda': 'Back',
            'hombro': 'Shoulders',
            'hombros': 'Shoulders',
            'pierna': 'Legs',
            'piernas': 'Legs',
            'biceps': 'Biceps',
            'triceps': 'Triceps',
            'core': 'Core'
        }
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for matching - remove accents and handle variations."""
        # Remove accents
        accent_map = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
            'ñ': 'n', 'Ñ': 'N'
        }
        for accented, unaccented in accent_map.items():
            text = text.replace(accented, unaccented)
        return text.lower().strip()
        
    def _load_exercise_mappings(self, file_path: str) -> Dict[str, str]:
        """Load exercise name to ID mappings from instructions.md"""
        mappings = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    # Match pattern: * Exercise name es English Name | ID | optional notes
                    # Capture English name separately to avoid matching the pipe in it
                    match = re.match(r'\* (.+?) es (.+?) \| ([A-Z0-9a-f-]+)', line.strip())
                    if match:
                        exercise_name = match.group(1).strip()
                        exercise_id = match.group(3).strip()  # ID is now group 3
                        # Normalize the mapping key (remove accents, lowercase)
                        normalized_name = self._normalize_text(exercise_name)
                        mappings[normalized_name] = exercise_id
        except FileNotFoundError:
            print(f"Warning: {file_path} not found. Exercise ID resolution will be limited.")
        
        return mappings

    def _translate_routine_focus(self, routine_focus: str) -> str:
        """Translate Spanish muscle-group routine labels to English."""
        normalized_focus = self._normalize_text(routine_focus)
        if not normalized_focus:
            return ""

        translated_focus = normalized_focus
        separator_map = {
            r'\s+\+\s+': ' + ',
            r'\s+y\s+': ' and ',
            r'\s+e\s+': ' and ',
            r'\s*/\s*': ' / '
        }
        for pattern, replacement in separator_map.items():
            translated_focus = re.sub(pattern, replacement, translated_focus)

        for spanish_term, english_term in sorted(
            self.routine_title_keyword_map.items(),
            key=lambda item: len(item[0]),
            reverse=True
        ):
            translated_focus = re.sub(
                rf'\b{re.escape(spanish_term)}\b',
                english_term,
                translated_focus,
                flags=re.IGNORECASE
            )

        translated_focus = re.sub(r'\s+', ' ', translated_focus).strip(' -–:')
        parts = re.split(r'( \+ | and | / )', translated_focus)
        formatted_parts = []
        for part in parts:
            if part in {' + ', ' and ', ' / '}:
                formatted_parts.append(part)
                continue

            mapped_term = self.routine_title_keyword_map.get(part.lower())
            if mapped_term:
                formatted_parts.append(mapped_term)
            else:
                formatted_parts.append(' '.join(word.capitalize() for word in part.split()))

        translated_focus = ''.join(formatted_parts).strip()
        return translated_focus or routine_focus.strip()

    def _translate_routine_title(self, routine_title: str) -> str:
        """Translate incoming Spanish routine titles to English titles for saved routines."""
        match = self.ROUTINE_TITLE_PATTERN.match(routine_title.strip())
        if not match:
            return routine_title.strip()

        day_number = match.group(2)
        routine_focus = match.group(3).strip()
        translated_focus = self._translate_routine_focus(routine_focus)
        if translated_focus:
            return f"Day {day_number} - {translated_focus}"
        return f"Day {day_number}"
    
    def _find_exercise_id(self, exercise_name: str) -> Optional[str]:
        """Find exercise ID by name (fuzzy matching)."""
        exercise_lower = self._normalize_text(exercise_name)
        
        # Normalize common variations
        exercise_lower = exercise_lower.replace('cristos', 'cristo')
        exercise_lower = exercise_lower.replace('dominada', 'dominadas')
        # Singular/plural normalization for common words
        exercise_lower = exercise_lower.replace('martillo ', 'martillos ')
        exercise_lower = exercise_lower.replace('extension ', 'extension ')
        
        # Special cases with direct mapping
        if 'dominadas' in exercise_lower and 'asistidas' not in exercise_lower:
            # Default dominadas to assisted
            return '2C37EC5E'
        
        # Direct match
        for mapped_name, exercise_id in self.exercise_mappings.items():
            if exercise_lower == mapped_name:
                return exercise_id
        
        # Partial match - look for key words
        best_match = None
        best_score = 0
        
        for mapped_name, exercise_id in self.exercise_mappings.items():
            # Check if mapped_name is a substring
            if mapped_name in exercise_lower or exercise_lower in mapped_name:
                # Prefer longer matches
                score = len(mapped_name)
                if score > best_score:
                    best_score = score
                    best_match = exercise_id
                continue
            
            # Word-based matching
            exercise_words = set(exercise_lower.split())
            mapped_words = set(mapped_name.split())
            
            matching_words = exercise_words & mapped_words
            score = len(matching_words)
            
            if score > best_score and score >= 2:
                best_score = score
                best_match = exercise_id
        
        return best_match
    
    def _parse_sets_reps(self, description: str) -> Dict:
        """
        Parse set/rep description into structured format.
        
        Examples:
          "4x6-8rep. (85% o más)" -> {sets: 4, reps_min: 6, reps_max: 8, intensity: "85%+"}
          "3x15rep. (moderado peso 80%)" -> {sets: 3, reps: 15, intensity: "80%"}
          "2 vuelta x sistema Drop set (6rep. + 6rep. + 8rep. + 10rep.)" -> dropset pattern
        """
        result = {
            'sets': 0,
            'reps': 0,
            'reps_min': None,
            'reps_max': None,
            'intensity': None,
            'is_dropset': False,
            'dropset_reps': []
        }
        
        # Extract intensity
        intensity_match = re.search(r'(\d+)%', description)
        if intensity_match:
            result['intensity'] = f"{intensity_match.group(1)}%"
        
        # Check for drop set
        if 'drop set' in description.lower() or 'dropset' in description.lower():
            result['is_dropset'] = True
            # Extract dropset reps: "6rep. + 6rep. + 8rep. + 10rep."
            dropset_pattern = re.findall(r'(\d+)rep\.', description)
            if dropset_pattern:
                result['dropset_reps'] = [int(r) for r in dropset_pattern]
                result['sets'] = 1  # Drop sets count as 1 "round"
                return result
        
        # Standard format: "4x6-8rep" or "3x15rep"
        sets_reps_match = re.search(r'(\d+)\s*x\s*(\d+)(?:-(\d+))?rep', description.lower())
        if sets_reps_match:
            result['sets'] = int(sets_reps_match.group(1))
            result['reps_min'] = int(sets_reps_match.group(2))
            
            if sets_reps_match.group(3):
                result['reps_max'] = int(sets_reps_match.group(3))
                # Use max value per ROUTINE_CREATION_RULES.md
                result['reps'] = result['reps_max']
            else:
                result['reps'] = result['reps_min']

        # Cluster fallback from manifesto rule:
        # "cluster" => 30s rest and minimum 3 sets of 6 reps when not specified
        if result['sets'] == 0 and 'cluster' in description.lower():
            result['sets'] = 3
            result['reps'] = 6
        
        return result

    def _is_mixed_muscle_core_title(self, routine_title: str) -> bool:
        """Detect titles like 'Espalda + Core' to avoid global Core overrides."""
        normalized_title = self._normalize_text(routine_title)
        if 'core' not in normalized_title:
            return False
        return any(keyword in normalized_title for keyword in self.muscle_group_keywords)

    def _is_core_routine_title(self, routine_title: str) -> bool:
        """Detect Core-only routine titles (e.g., 'D1 Core', 'Day 7 - Core')."""
        normalized_title = self._normalize_text(routine_title)
        if 'core' not in normalized_title:
            return False
        return not any(keyword in normalized_title for keyword in self.muscle_group_keywords)

    def _is_explicit_core_time_exercise(self, exercise_name: str, description_line: str) -> bool:
        """Return True only when exercise is explicitly Core and explicitly time-based."""
        normalized_name = self._normalize_text(exercise_name)
        normalized_description = self._normalize_text(description_line)
        combined_text = f"{normalized_name} {normalized_description}"

        is_core_exercise = any(keyword in combined_text for keyword in self.core_keywords)
        has_time_marker = bool(re.search(r'\d+\s*(seg|sec|s|min|mins|minuto|minutos)', combined_text))
        has_time_word = any(marker in combined_text for marker in ['tiempo', 'duracion', 'duration'])

        return is_core_exercise and (has_time_marker or has_time_word)

    def _determine_rest_seconds(self, routine_title: str, exercise_name: str, description_line: str) -> int:
        """Apply rest policy with Core routine override (2 series/20s handled elsewhere)."""
        combined_text = self._normalize_text(f"{exercise_name} {description_line}")

        if self._is_core_routine_title(routine_title):
            return 20

        if 'cluster' in combined_text:
            return 30

        if self._is_explicit_core_time_exercise(exercise_name, description_line):
            return 20

        if self._is_mixed_muscle_core_title(routine_title):
            return 60

        return 60
    
    def _create_sets_array(self, sets_info: Dict, exercise_name: str, routine_title: str) -> List[Dict]:
        """Create sets array based on parsed information and routine-level policies."""
        sets = []
        is_core_routine = self._is_core_routine_title(routine_title)
        
        # Check if exercise requires doubled reps
        needs_doubling = any(keyword in exercise_name.lower() 
                            for keyword in ['alternado', 'individual', 'desplantes'])
        
        # Warmup set (non-Core only)
        if not is_core_routine:
            warmup_reps = 24 if needs_doubling else 12
            sets.append({
                "type": "warmup",
                "weight_kg": 0,
                "reps": warmup_reps,
                "distance_meters": None,
                "duration_seconds": None,
                "custom_metric": None
            })
        
        # Drop set
        if (not is_core_routine) and sets_info['is_dropset'] and sets_info['dropset_reps']:
            for reps in sets_info['dropset_reps']:
                final_reps = reps * 2 if needs_doubling else reps
                sets.append({
                    "type": "dropset",
                    "weight_kg": 0,
                    "reps": final_reps,
                    "distance_meters": None,
                    "duration_seconds": None,
                    "custom_metric": None
                })
        else:
            # Normal sets
            if sets_info['reps']:
                reps = sets_info['reps']
            elif is_core_routine:
                reps = 0
            else:
                reps = 12

            if needs_doubling:
                reps *= 2

            target_sets = 2 if is_core_routine else sets_info['sets']
            
            for _ in range(target_sets):
                sets.append({
                    "type": "normal",
                    "weight_kg": 0,
                    "reps": reps,
                    "distance_meters": None,
                    "duration_seconds": None,
                    "custom_metric": None
                })
        
        return sets
    
    def _parse_exercise_block(self, lines: List[str], routine_title: str) -> Optional[Dict]:
        """
        Parse an exercise block.
        
        Expected format:
          Ejercicio 1 - 4x6-8rep. (85% o más)
          1-Press de pecho en banca plana
        """
        if len(lines) < 2:
            return None
        
        # Line 1: Exercise number and sets/reps
        description_line = lines[0].strip()
        sets_info = self._parse_sets_reps(description_line)
        
        # Line 2: Exercise name
        exercise_line = lines[1].strip()
        # Remove leading number/dash if present: "1-Press..." -> "Press..."
        exercise_name = re.sub(r'^\d+\s*-\s*', '', exercise_line)
        
        # Find exercise ID
        exercise_id = self._find_exercise_id(exercise_name)
        rest_seconds = self._determine_rest_seconds(routine_title, exercise_name, description_line)
        
        # Create exercise object
        exercise = {
            "exercise_template_id": exercise_id or "",
            "superset_id": None,
            "rest_seconds": rest_seconds,
            "notes": f"{exercise_name} - {description_line.split('-', 1)[1].strip() if '-' in description_line else description_line}",
            "sets": self._create_sets_array(sets_info, exercise_name, routine_title)
        }
        
        return exercise
    
    def parse_text_file(self, file_path: str) -> List[Dict]:
        """
        Parse a text file containing multiple routine descriptions.
        
        Expected format:
                    Día 1 – PECHO Y HOMBRO
          PECHO 4
          Ejercicio 1 - 4x6-8rep. (85% o más)
          1-Press de pecho en banca plana
          Ejercicio 2 - 4x12rep. (moderado peso 80%)
          3-Cristo con mancuerna
          ...
          
                    Día 2 – ESPALDA + CORE
          ...

                Saved routine titles are translated to English, e.g. "Day 1 - Chest and Shoulders".
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        routines = []
        current_routine = None
        current_exercises = []
        exercise_lines = []
        
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Check for new routine title and save the English title variant
            if self.ROUTINE_TITLE_PATTERN.match(line):
                # Save previous routine if exists
                if current_routine and current_exercises:
                    current_routine['exercises'] = current_exercises
                    routines.append({"routine": current_routine})
                
                # Start new routine
                current_routine = {
                    "title": self._translate_routine_title(line),
                    "folder_id": self.folder_id,
                    "exercises": []
                }
                current_exercises = []
                exercise_lines = []
                continue
            
            # Skip section headers (e.g., "PECHO 4", "BÍCEPS 4")
            if re.match(r'^[A-ZÁÉÍÓÚ\s]+\d+$', line):
                continue
            
            # Check for exercise start
            if line.startswith('Ejercicio'):
                # Parse previous exercise if exists
                if exercise_lines and current_routine:
                    exercise = self._parse_exercise_block(
                        exercise_lines,
                        current_routine.get('title', '')
                    )
                    if exercise:
                        current_exercises.append(exercise)
                
                # Start new exercise
                exercise_lines = [line]
            elif exercise_lines:
                # Add line to current exercise
                exercise_lines.append(line)
        
        # Parse last exercise
        if exercise_lines and current_routine:
            exercise = self._parse_exercise_block(
                exercise_lines,
                current_routine.get('title', '')
            )
            if exercise:
                current_exercises.append(exercise)
        
        # Save last routine
        if current_routine and current_exercises:
            current_routine['exercises'] = current_exercises
            routines.append({"routine": current_routine})
        
        return routines
    
    def save_batch_json(self, routines: List[Dict], output_file: str):
        """Save routines to batch JSON format."""
        batch_data = {"routines": routines}
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(batch_data, f, indent=2, ensure_ascii=False)
    
    def print_summary(self, routines: List[Dict]):
        """Print parsing summary."""
        print(f"\n{'='*70}")
        print("📋 PARSING SUMMARY")
        print(f"{'='*70}\n")
        
        print(f"Total routines parsed: {len(routines)}\n")
        
        missing_ids = []
        
        for i, routine_data in enumerate(routines, 1):
            routine = routine_data['routine']
            title = routine.get('title', 'Unknown')
            exercises = routine.get('exercises', [])
            
            print(f"[{i}] {title}")
            print(f"    Exercises: {len(exercises)}")
            
            # Check for missing IDs
            for j, exercise in enumerate(exercises, 1):
                if not exercise['exercise_template_id']:
                    exercise_notes = exercise.get('notes', 'Unknown exercise')
                    missing_ids.append({
                        'routine': title,
                        'exercise_num': j,
                        'description': exercise_notes
                    })
            
            print()
        
        if missing_ids:
            print(f"⚠️  WARNING: {len(missing_ids)} exercise(s) missing IDs:")
            for item in missing_ids:
                print(f"   [{item['routine']}] Exercise {item['exercise_num']}: {item['description']}")
            print("\n   Review and add missing exercises to instructions.md")
            print("   Or use: python exercise_validator.py --interactive <output_file>")
        else:
            print("✅ All exercises have IDs!")
        
        print()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Parse plain text routine descriptions to JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse text file to JSON
  %(prog)s routines.txt -o extracted_routines.json
  
  # Parse and show summary without saving
  %(prog)s routines.txt --dry-run
  
Expected input format:
  Día 1 – PECHO Y HOMBRO
  PECHO 4
  Ejercicio 1 - 4x6-8rep. (85% o más)
  1-Press de pecho en banca plana
  Ejercicio 2 - 4x12rep. (moderado peso 80%)
  3-Cristo con mancuerna
  
  Día 2 – ESPALDA + CORE
  ...
        """
    )
    
    parser.add_argument('input_file', help='Text file with routine descriptions')
    parser.add_argument('-o', '--output', default='extracted_routines.json',
                       help='Output JSON file (default: extracted_routines.json)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Parse and show summary without saving')
    parser.add_argument('--mappings', default='instructions.md',
                       help='Exercise mappings file (default: instructions.md)')
    
    args = parser.parse_args()
    
    # Validate input file
    if not Path(args.input_file).exists():
        print(f"❌ File not found: {args.input_file}")
        sys.exit(1)
    
    try:
        # Parse file
        print(f"📂 Parsing: {args.input_file}\n")
        parser = RoutineTextParser(args.mappings)
        routines = parser.parse_text_file(args.input_file)
        
        # Print summary
        parser.print_summary(routines)
        
        # Save if not dry run
        if not args.dry_run:
            parser.save_batch_json(routines, args.output)
            print(f"💾 Saved to: {args.output}")
            print(f"\nNext step:")
            print(f"  venv/bin/python batch_routine_uploader.py {args.output} --dry-run")
        else:
            print("🔍 Dry run - no file saved")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
