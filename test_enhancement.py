#!/Users/axelcaballero/projects/hevy/routine-uploader/venv/bin/python
"""
Test script to demonstrate the routine enhancement functionality.
This tests without needing API access.
"""

import json
from routine_enhancer import RoutineEnhancer
from hevy_api_client import HevyAPIClient


class MockHevyAPIClient(HevyAPIClient):
    """Mock API client for testing without actual API calls"""
    
    def get_exercise_history(self, exercise_template_id: str):
        """Return mock exercise history"""
        # Mock data simulating real warmup history
        mock_histories = {
            "37FCC2BB": {  # Barbell Curl
                "exercise_history": [
                    {
                        "set_type": "warmup",
                        "weight_kg": 15.0,
                        "reps": 12,
                        "workout_start_time": "2025-01-15T10:00:00Z"
                    },
                    {
                        "set_type": "warmup",
                        "weight_kg": 14.5,
                        "reps": 12,
                        "workout_start_time": "2025-01-14T10:00:00Z"
                    },
                    {
                        "set_type": "warmup",
                        "weight_kg": 15.5,
                        "reps": 12,
                        "workout_start_time": "2025-01-12T10:00:00Z"
                    },
                ]
            },
            "7E3BC8B6": {  # Tricep exercise
                "exercise_history": [
                    {
                        "set_type": "warmup",
                        "weight_kg": 12.0,
                        "reps": 12,
                        "workout_start_time": "2025-01-15T11:00:00Z"
                    },
                    {
                        "set_type": "warmup",
                        "weight_kg": 11.5,
                        "reps": 12,
                        "workout_start_time": "2025-01-14T11:00:00Z"
                    },
                ]
            }
        }
        return mock_histories.get(exercise_template_id, {"exercise_history": []})


def test_enhancement():
    """Test the enhancement functionality"""
    
    print("=" * 60)
    print("🧪 Testing Routine Enhancement")
    print("=" * 60)
    
    # Load the template
    with open('input/dia_10_biceps_triceps.json', 'r') as f:
        original_routine = json.load(f)
    
    print("\n📋 Original Routine:")
    routine = original_routine['routine']
    print(f"   Title: {routine['title']}")
    print(f"   Exercises: {len(routine['exercises'])}")
    
    # Show original warmup weights
    print("\n   Original warmup weights:")
    for i, ex in enumerate(routine['exercises'][:2]):
        ex_id = ex['exercise_template_id']
        warmup_set = ex['sets'][0]
        print(f"      Exercise {i+1} ({ex_id}): {warmup_set['weight_kg']}kg")
    
    # Create enhancer with mock client
    mock_client = MockHevyAPIClient(api_key="fake_key_for_testing")
    enhancer = RoutineEnhancer(api_client=mock_client)
    
    # Enhance the routine
    print("\n🔄 Enhancing routine...")
    enhanced_routine = enhancer.enhance_routine(
        original_routine,
        warmup_strategy="recent",
        verbose=True
    )
    
    # Show enhanced warmup weights
    print("\n✨ Enhanced warmup weights:")
    enhanced = enhanced_routine['routine']
    for i, ex in enumerate(enhanced['exercises'][:2]):
        ex_id = ex['exercise_template_id']
        warmup_set = ex['sets'][0]
        print(f"      Exercise {i+1} ({ex_id}): {warmup_set['weight_kg']}kg")
    
    # Verify changes
    print("\n✅ Verification:")
    for i, (orig_ex, enh_ex) in enumerate(zip(routine['exercises'][:2], enhanced['exercises'][:2])):
        orig_weight = orig_ex['sets'][0]['weight_kg']
        enh_weight = enh_ex['sets'][0]['weight_kg']
        if orig_weight == 0 and enh_weight > 0:
            print(f"   Exercise {i+1}: ✓ Updated from {orig_weight}kg to {enh_weight}kg")
        else:
            print(f"   Exercise {i+1}: Unchanged (was {orig_weight}kg, still {enh_weight}kg)")
    
    print("\n" + "=" * 60)
    print("✅ Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    test_enhancement()
