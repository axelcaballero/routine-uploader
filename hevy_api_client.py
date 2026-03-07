#!/Users/axelcaballero/projects/hevy/routine-uploader/venv/bin/python
"""
Hevy API Client for creating and managing workout routines.
Documentation: https://api.hevy.io/docs
"""

import os
import json
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class HevyAPIClient:
    """Client for interacting with the Hevy API"""
    
    BASE_URL = "https://api.hevyapp.com"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Hevy API client.
        
        Args:
            api_key: Hevy API key. If not provided, will look for HEVY_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("HEVY_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "API key not provided. Set HEVY_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json",
        }
        self._folder_cache: Dict[str, Dict[str, Any]] = {}
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the Hevy API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (e.g., "/routines")
            data: Request body data
            params: Query parameters
            
        Returns:
            Response JSON data
            
        Raises:
            Exception: If request fails
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_msg = f"API Error: {e.response.status_code} - {e.response.text}"
            raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def create_routine(self, routine_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new workout routine.
        
        Args:
            routine_data: Routine data in the format:
                {
                    "routine": {
                        "title": str,
                        "folder_id": Optional[str],
                        "notes": Optional[str],
                        "exercises": [
                            {
                                "exercise_template_id": str,
                                "superset_id": Optional[str],
                                "rest_seconds": int,
                                "notes": Optional[str],
                                "sets": [
                                    {
                                        "type": "normal|warmup|dropset",
                                        "weight_kg": float,
                                        "reps": int,
                                        "distance_meters": Optional[float],
                                        "duration_seconds": Optional[int],
                                        "custom_metric": Optional[Any]
                                    }
                                ]
                            }
                        ]
                    }
                }
        
        Returns:
            Created routine response
        """
        return self._make_request("POST", "/v1/routines", data=routine_data)
    
    def get_routine(self, routine_id: str) -> Dict[str, Any]:
        """
        Get a routine by ID.
        
        Args:
            routine_id: The routine ID
            
        Returns:
            Routine data
        """
        return self._make_request("GET", f"/v1/routines/{routine_id}")
    
    def list_routines(self, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        List all routines for the authenticated user.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of routines per page
        
        Returns:
            List of routines with pagination info
        """
        return self._make_request("GET", "/v1/routines", params={"page": page, "page_size": page_size})
    
    def create_routine_folder(self, folder_title: str) -> Dict[str, Any]:
        """
        Create a new routine folder.
        
        Args:
            folder_title: Title for the new folder
            
        Returns:
            Created folder response with folder ID
        """
        data = {
            "routine_folder": {
                "title": folder_title
            }
        }
        return self._make_request("POST", "/v1/routine_folders", data=data)
    
    def list_routine_folders(self, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        List all routine folders.
        
        Args:
            page: Page number (default: 1)
            page_size: Number of results per page (default: 10)
            
        Returns:
            List of routine folders
        """
        params = {"page": page, "pageSize": page_size}
        return self._make_request("GET", "/v1/routine_folders", params=params)
    
    def get_routine_folder(self, folder_id: str) -> Dict[str, Any]:
        """
        Get a routine folder by ID.
        
        Args:
            folder_id: The folder ID
            
        Returns:
            Folder data
        """
        return self._make_request("GET", f"/v1/routine_folders/{folder_id}")

    def find_routine_folder_by_title(
        self,
        folder_title: str,
        page_size: int = 10
    ) -> Optional[Dict[str, Any]]:
        """
        Find an existing routine folder by title.

        Args:
            folder_title: Folder title to search for
            page_size: Number of folders to fetch per page

        Returns:
            Folder object if found, otherwise None
        """
        normalized_title = folder_title.strip().casefold()
        page_size = min(max(1, page_size), 10)
        page = 1

        while True:
            response = self.list_routine_folders(page=page, page_size=page_size)
            folders = response.get("routine_folders", [])

            for folder in folders:
                existing_title = str(folder.get("title", "")).strip().casefold()
                if existing_title == normalized_title:
                    return folder

            if len(folders) < page_size:
                break

            page += 1

        return None

    def ensure_routine_folder(self, folder_title: str) -> Dict[str, Any]:
        """
        Ensure a routine folder exists, creating it if needed.

        Args:
            folder_title: Folder title to find or create

        Returns:
            Folder object
        """
        cache_key = folder_title.strip().casefold()
        cached_folder = self._folder_cache.get(cache_key)
        if cached_folder:
            return cached_folder

        existing_folder = self.find_routine_folder_by_title(folder_title)
        if existing_folder:
            self._folder_cache[cache_key] = existing_folder
            return existing_folder

        response = self.create_routine_folder(folder_title)
        created_folder = response.get("routine_folder")

        if isinstance(created_folder, dict):
            self._folder_cache[cache_key] = created_folder
            return created_folder

        if isinstance(created_folder, list) and created_folder:
            self._folder_cache[cache_key] = created_folder[0]
            return created_folder[0]

        raise Exception(f"Failed to create routine folder '{folder_title}'")

    def ensure_routine_folder_id(self, folder_title: str) -> Any:
        """
        Ensure a routine folder exists and return its ID.

        Args:
            folder_title: Folder title to find or create

        Returns:
            Folder ID
        """
        folder = self.ensure_routine_folder(folder_title)
        folder_id = folder.get("id")

        if not folder_id:
            raise Exception(f"Routine folder '{folder_title}' has no ID")

        return folder_id
    
    def update_routine(self, routine_id: str, routine_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing routine.
        
        Args:
            routine_id: The routine ID to update
            routine_data: Updated routine data
            
        Returns:
            Updated routine response
        """
        return self._make_request("PUT", f"/v1/routines/{routine_id}", data=routine_data)
    
    def delete_routine(self, routine_id: str) -> Dict[str, Any]:
        """
        Delete a routine.
        
        Args:
            routine_id: The routine ID to delete
            
        Returns:
            Deletion confirmation
        """
        return self._make_request("DELETE", f"/v1/routines/{routine_id}")
    
    def get_exercise_templates(self) -> Dict[str, Any]:
        """
        Get available exercise templates.
        
        Returns:
            List of available exercises
        """
        return self._make_request("GET", "/v1/exercise_templates")
    
    def get_exercise_history(self, exercise_template_id: str) -> Dict[str, Any]:
        """
        Get exercise history for a specific exercise template.
        
        Args:
            exercise_template_id: The exercise template ID
            
        Returns:
            Exercise history with all workouts for this exercise
        """
        return self._make_request("GET", f"/v1/exercise_history/{exercise_template_id}")
    
    def list_workouts(self, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        Get a paginated list of workouts.
        
        Args:
            page: Page number (default: 1, first page has most recent workouts)
            page_size: Number of results per page (default: 10)
            
        Returns:
            List of workouts with metadata
        """
        params = {"page": page, "pageSize": page_size}
        return self._make_request("GET", "/v1/workouts", params=params)
    
    def get_workout(self, workout_id: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific workout.
        
        Args:
            workout_id: The workout ID to retrieve
            
        Returns:
            Detailed workout object with all exercises and sets
        """
        return self._make_request("GET", f"/v1/workouts/{workout_id}")
    
    def update_workout(self, workout_id: str, description: str) -> Dict[str, Any]:
        """
        Update a workout's description/notes.
        
        The Hevy API requires the full workout object to be sent with the update.
        This method handles fetching the current workout, cleaning the data,
        and sending the update.
        
        Args:
            workout_id: The workout ID to update
            description: The description/notes to set
            
        Returns:
            Updated workout object with new description
            
        Raises:
            Exception: If the update fails
        """
        # Get the current workout data
        workouts = self.list_workouts(page=1, page_size=1)
        current_workout = None
        for w in workouts.get('workouts', []):
            if w.get('id') == workout_id:
                current_workout = w
                break
        
        if not current_workout:
            raise Exception(f"Workout {workout_id} not found")
        
        # Clean exercise data - remove index fields and ensure notes are non-empty
        exercises = []
        for ex in current_workout.get('exercises', []):
            clean_ex = {
                'exercise_template_id': ex.get('exercise_template_id'),
                'notes': ex.get('notes') or '-',  # Ensure notes is not empty
                'sets': []
            }
            
            for s in ex.get('sets', []):
                clean_set = {
                    'type': s.get('type'),
                    'weight_kg': s.get('weight_kg'),
                    'reps': s.get('reps'),
                    'distance_meters': s.get('distance_meters'),
                    'duration_seconds': s.get('duration_seconds'),
                    'custom_metric': s.get('custom_metric'),
                    'rpe': s.get('rpe')
                }
                clean_ex['sets'].append(clean_set)
            
            exercises.append(clean_ex)
        
        # Prepare the update payload with all required fields
        data = {
            'workout': {
                'title': current_workout.get('title'),
                'description': description,
                'start_time': current_workout.get('start_time'),
                'end_time': current_workout.get('end_time'),
                'exercises': exercises,
                'is_private': current_workout.get('is_private', False)
            }
        }
        
        response = self._make_request('PUT', f'/v1/workouts/{workout_id}', data=data)
        # Extract the workout object from the response (API returns nested structure)
        workout_list = response.get('workout', [])
        if isinstance(workout_list, list) and len(workout_list) > 0:
            return workout_list[0]
        return response
    
    def create_routine_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Create a routine from a JSON file.
        
        Args:
            file_path: Path to JSON file containing routine data
            
        Returns:
            Created routine response
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            routine_data = json.load(f)
        
        return self.create_routine(routine_data)
    
    def save_routine_to_file(self, routine_data: Dict[str, Any], file_path: str) -> None:
        """
        Save routine data to a JSON file.
        
        Args:
            routine_data: Routine data to save
            file_path: Path to save the file to
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(routine_data, f, indent=2, ensure_ascii=False)
        print(f"Routine saved to {file_path}")
    
    def get_warmup_weight_for_exercise(
        self, 
        exercise_template_id: str,
        strategy: str = "recent"
    ) -> Optional[float]:
        """
        Get a suggested warmup weight for an exercise based on exercise history.
        
        Args:
            exercise_template_id: The exercise template ID
            strategy: How to determine warmup weight:
                - "recent": Use the most recent warmup weight (default)
                - "average": Use the average of the last 5 warmup weights
                - "mode": Use the most common warmup weight
        
        Returns:
            Warmup weight in kg, or None if no warmup history exists
        """
        try:
            history = self.get_exercise_history(exercise_template_id)
            warmup_sets = [
                set_data for set_data in history.get('exercise_history', [])
                if set_data.get('set_type') == 'warmup' and set_data.get('weight_kg')
            ]
            
            if not warmup_sets:
                return None
            
            # Sort by most recent first (by workout_start_time)
            warmup_sets.sort(
                key=lambda x: x.get('workout_start_time', ''),
                reverse=True
            )
            
            if strategy == "recent":
                return warmup_sets[0].get('weight_kg')
            
            elif strategy == "average":
                # Average of last 5 warmup sets
                recent_warmups = [s.get('weight_kg') for s in warmup_sets[:5]]
                return sum(recent_warmups) / len(recent_warmups) if recent_warmups else None
            
            elif strategy == "mode":
                # Most common warmup weight
                from collections import Counter
                weights = [s.get('weight_kg') for s in warmup_sets[:10]]
                if weights:
                    counter = Counter(weights)
                    return counter.most_common(1)[0][0]
                return None
            
            return None
        except Exception:
            # If there's any error fetching history, return None
            return None


def main():
    """Example usage of the HevyAPIClient"""
    
    # Initialize the client
    try:
        client = HevyAPIClient()
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    print("Hevy API Client initialized successfully!")
    
    # Example: List available exercise templates
    print("\nFetching available exercise templates...")
    try:
        templates = client.get_exercise_templates()
        print(f"Found {len(templates.get('exercises', []))} exercise templates")
    except Exception as e:
        print(f"Error fetching templates: {e}")
    
    # Example: List existing routines
    print("\nFetching your routines...")
    try:
        routines = client.list_routines()
        print(f"Found {len(routines.get('routines', []))} routines")
        for routine in routines.get('routines', [])[:3]:  # Show first 3
            print(f"  - {routine.get('title')}")
    except Exception as e:
        print(f"Error fetching routines: {e}")


if __name__ == "__main__":
    main()
