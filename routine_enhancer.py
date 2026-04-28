#!/usr/bin/env python3
"""
Routine Template Enhancer
Automatically populates missing warmup weights and reps for new routine templates
by looking up historical data from existing workouts.
"""

import json
from typing import Dict, Any, Optional
from hevy_api_client import HevyAPIClient


class RoutineEnhancer:
    """Enhances routine templates with data from exercise history"""
    
    def __init__(self, api_client: Optional[HevyAPIClient] = None):
        """
        Initialize the routine enhancer.
        
        Args:
            api_client: HevyAPIClient instance. If None, creates a new one.
        """
        self.client = api_client or HevyAPIClient()
    
    def enhance_routine(
        self,
        routine_data: Dict[str, Any],
        warmup_strategy: str = "recent",
        warmup_reps: Optional[int] = None,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Enhance a routine template by populating missing warmup data.
        
        Args:
            routine_data: The routine template data
            warmup_strategy: Strategy for choosing warmup weight ("recent", "average", "mode")
            warmup_reps: Default reps for warmup sets. If None, uses reps from history.
            verbose: If True, print details about what's being populated
            
        Returns:
            Enhanced routine data with warmup weights and reps populated
        """
        enhanced_routine = json.loads(json.dumps(routine_data))  # Deep copy
        
        routine = enhanced_routine.get('routine', {})
        exercises = routine.get('exercises', [])
        
        for exercise in exercises:
            exercise_template_id = exercise.get('exercise_template_id')
            if not exercise_template_id:
                continue
            
            sets = exercise.get('sets', [])
            
            # Find warmup sets with missing weight
            for set_idx, set_data in enumerate(sets):
                if set_data.get('type') == 'warmup':
                    # Check if weight is missing or zero
                    current_weight = set_data.get('weight_kg', 0)
                    if current_weight == 0 or current_weight is None:
                        # Try to get warmup weight from history
                        warmup_weight = self.client.get_warmup_weight_for_exercise(
                            exercise_template_id,
                            strategy=warmup_strategy
                        )
                        
                        if warmup_weight is not None:
                            set_data['weight_kg'] = round(warmup_weight, 2)
                            if verbose:
                                print(f"  ✓ Set {set_idx + 1}: Populated warmup weight = {warmup_weight:.2f}kg")
                        else:
                            if verbose:
                                print(f"  ⚠ Set {set_idx + 1}: No warmup history found")
                    
                    # Handle missing reps if provided
                    if warmup_reps is not None and (set_data.get('reps', 0) == 0 or set_data.get('reps') is None):
                        set_data['reps'] = warmup_reps
                        if verbose:
                            print(f"  ✓ Set {set_idx + 1}: Set warmup reps = {warmup_reps}")
        
        return enhanced_routine
    
    def enhance_from_file(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        warmup_strategy: str = "recent",
        warmup_reps: Optional[int] = None,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Enhance a routine template from a file.
        
        Args:
            input_path: Path to input routine template JSON file
            output_path: Path to save enhanced routine. If None, overwrites input_path
            warmup_strategy: Strategy for choosing warmup weight
            warmup_reps: Default reps for warmup sets
            verbose: If True, print details
            
        Returns:
            Enhanced routine data
        """
        # Read the routine template
        with open(input_path, 'r', encoding='utf-8') as f:
            routine_data = json.load(f)
        
        routine_title = routine_data.get('routine', {}).get('title', 'Unknown')
        if verbose:
            print(f"\n📋 Enhancing routine: {routine_title}")
        
        # Enhance the routine
        enhanced = self.enhance_routine(
            routine_data,
            warmup_strategy=warmup_strategy,
            warmup_reps=warmup_reps,
            verbose=verbose
        )
        
        # Save the enhanced routine
        save_path = output_path or input_path
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(enhanced, f, indent=2, ensure_ascii=False)
        
        if verbose:
            print(f"✅ Enhanced routine saved to: {save_path}")
        
        return enhanced


def main():
    """Main entry point for routine enhancement"""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(
        description="Enhance routine templates with historical workout data"
    )
    parser.add_argument(
        "input_file",
        help="Path to routine template JSON file"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: overwrites input file)"
    )
    parser.add_argument(
        "-s", "--strategy",
        choices=["recent", "average", "mode"],
        default="recent",
        help="Strategy for choosing warmup weight (default: recent)"
    )
    parser.add_argument(
        "-r", "--reps",
        type=int,
        help="Set warmup reps to this value (default: don't modify)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print detailed progress information"
    )
    
    args = parser.parse_args()
    
    try:
        enhancer = RoutineEnhancer()
        enhancer.enhance_from_file(
            input_path=args.input_file,
            output_path=args.output,
            warmup_strategy=args.strategy,
            warmup_reps=args.reps,
            verbose=args.verbose or True  # Default to verbose for CLI
        )
    except FileNotFoundError:
        print(f"❌ Error: File not found - {args.input_file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
