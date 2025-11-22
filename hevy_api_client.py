#!/usr/bin/env python3
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
