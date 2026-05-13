#!/usr/bin/env python3
"""
Add warmup sets to all 12 routines in HSF 13 folder.
Run after rate limit cooldown: python add_warmup_sets.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hevy_api_client import HevyAPIClient
import time

# All routine IDs from recent upload
ROUTINE_IDS = [
    ("250cb865-39f7-4442-b098-6ba032d1835b", "Día 1 – Pecho y Hombro"),
    ("3ebde1c2-9b87-49a1-a76c-3cfbcc3511a5", "Día 2 – Espalda"),
    ("e4e4da13-721f-4958-b352-037b51883f10", "Día 3 – Pierna"),
    ("28e3664c-9068-4785-b13c-bb3ac61f55c1", "Día 4 – Bíceps y Tríceps"),
    ("a7c7d91f-d8f9-4b6f-a1b2-cb805e846761", "Día 5 – Pecho y Hombro"),
    ("70c7dd1c-fdfe-4fa2-9113-cbf5c4cf99c0", "Día 6 – Pierna"),
    ("6458f34b-18c6-4951-bed1-82638cda1b22", "Día 7 – Espalda y Hombro"),
    ("41bf57b8-077e-4111-a233-3230dfc65536", "Día 8 – Pecho"),
    ("a4d8c17f-d8da-4e8a-90e2-45c829fc6c66", "Día 9 – Pierna"),
    ("eec3e63d-eae8-45ec-a0f0-389893066e10", "Día 10 – Bíceps y Tríceps"),
    ("804f165a-3f87-49f3-942f-a5f144811e99", "Día 11 – Hombro y Espalda"),
    ("3fb5aecb-a63b-477a-9b07-e5f56357c09d", "Día 12 – Pierna")
]

# Exercises requiring 24 reps warmup (from ROUTINE_CREATION_RULES.md Rule 3)
DUPLICATE_REPS_EXERCISES = {
    "37FCC2BB",  # Curl Alternado con mancuerna
    "FAB6EB2F",  # Predicador banca Scott con mancuerna individual
    "8293E554",  # Elevación frontal con mancuerna (if marked "individual")
    "F1E57334",  # Jalón mancuerna
    "D0C4A899",  # Jalón en polea alta
    "0d2c58fa-8cf3-4e4d-ac1c-c6db5262d972",  # Desplantes búlgaros
    "B537D09F",  # Desplantes recorridos con mancuerna
    "6E6EE645",  # Desplantes fijos con barra
    "724CDE60",  # Concentrado con mancuerna
    "7E3BC8B6",  # Martillos dobles
    "DE68C825",  # Elevación lateral alternas con polea baja
}

def main():
    client = HevyAPIClient()
    
    print("="*70)
    print("🔧 ADDING WARMUP SETS TO ALL 12 ROUTINES")
    print("="*70)
    print("\n⚠️  This will take ~60 seconds (3s delay between requests)")
    print()
    
    success_count = 0
    error_count = 0
    
    for i, (routine_id, routine_name) in enumerate(ROUTINE_IDS):
        try:
            print(f"[{i+1}/12] {routine_name}...", end=" ", flush=True)
            
            # Get current routine
            response = client.get_routine(routine_id)
            routine = response['routine']
            
            warmups_added = 0
            
            # Add warmup set to each exercise
            for exercise in routine['exercises']:
                exercise_id = exercise['exercise_template_id']
                
                # Check if already has warmup
                if exercise['sets'] and exercise['sets'][0].get('type') == 'warmup':
                    continue
                
                # Determine warmup reps (12 or 24)
                warmup_reps = 24 if exercise_id in DUPLICATE_REPS_EXERCISES else 12
                
                # Create and insert warmup set
                warmup_set = {
                    "type": "warmup",
                    "weight_kg": None,
                    "reps": warmup_reps,
                    "distance_meters": None,
                    "duration_seconds": None
                }
                
                exercise['sets'].insert(0, warmup_set)
                warmups_added += 1
            
            # Prepare update data (no folder_id in updates)
            exercises_data = []
            for exercise in routine['exercises']:
                ex_data = {
                    "exercise_template_id": exercise['exercise_template_id'],
                    "superset_id": exercise['superset_id'],
                    "rest_seconds": exercise['rest_seconds'],
                    "notes": exercise['notes'],
                    "sets": [
                        {
                            "type": s['type'],
                            "weight_kg": s['weight_kg'],
                            "reps": s['reps'],
                            "distance_meters": s['distance_meters'],
                            "duration_seconds": s['duration_seconds']
                        }
                        for s in exercise['sets']
                    ]
                }
                exercises_data.append(ex_data)
            
            update_data = {
                "routine": {
                    "title": routine['title'],
                    "exercises": exercises_data
                }
            }
            
            # Update routine
            client.update_routine(routine_id, update_data)
            print(f"✅ {warmups_added} warmup sets added")
            success_count += 1
            
            # Rate limit protection: wait 3 seconds between requests
            if i < len(ROUTINE_IDS) - 1:
                time.sleep(3)
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                print(f"❌ Rate limit hit, waiting 10s...")
                time.sleep(10)
            else:
                print(f"❌ Error: {error_msg[:50]}")
            error_count += 1
            time.sleep(5)
    
    print("\n" + "="*70)
    print("📊 FINAL RESULT")
    print("="*70)
    print(f"✅ Successfully updated: {success_count}/12")
    print(f"❌ Failed: {error_count}/12")
    print("="*70)
    
    if error_count > 0:
        print("\n⚠️  Some routines failed. Wait 5 minutes and run again.")
    else:
        print("\n🎉 All routines now have warmup sets!")

if __name__ == "__main__":
    main()
