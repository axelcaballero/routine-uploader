# Routine Folder Management Guide

## Quick Commands

### View All Folders & Most Recent
```bash
python scripts/get_recent_folder.py
```

### Create New Folder (Auto-Incremented)
```bash
# Automatically determines next folder name and asks for confirmation
# E.g., HSF 15 -> HSF 16
python scripts/create_new_folder.py
```

### Create Folder with Custom Name
```bash
python scripts/folder_manager.py create "Custom Folder Name"
```

### Upload to Specific Folder
```bash
# Single routine
python routine_uploader.py input/dia_7_espalda.json --folder-title "HSF 15"

# Batch upload
python scripts/batch_routine_uploader.py extracted_routines.json --folder-title "HSF 15"
```

### Create New Folder
```bash
python scripts/folder_manager.py create "HSF 16"
```

## Current Routine Folders

| Rank | Name | ID | Purpose |
|------|------|----|---------|
| 1 | **HSF 15** | 2482205 | Current (most recent) |
| 2 | HSF 14 | 2262799 | Previous cycle |
| 3 | HSF 13 | 1986567 | Archive |
| 4 | HSF 12 | 1812915 | Archive |
| 5 | HSF 11 | 1665240 | Archive |
| 6-10 | HSF 10-6 | Various | Older cycles |

## Understanding Folder Structure

### Folder Index
- **Index 0**: Most recent folder (appears first in API responses)
- **Index 1-9**: Older folders in reverse chronological order
- Displayed in the `scripts/get_recent_folder.py` output

### When to Update
- When uploading a new routine: Use the current folder (HSF 15)
- When creating a new cycle: Create a new folder with the next number (HSF 16)
- When organizing old routines: Use archive folders for reference

## Available Scripts & Commands

### `scripts/get_recent_folder.py`
**Purpose:** Display all folders ranked by recency
**Usage:** `python scripts/get_recent_folder.py`

### `scripts/folder_manager.py`
**Purpose:** Manage folders via CLI
**Commands:**
```bash
# List all folders
python scripts/folder_manager.py list

# Create new folder
python scripts/folder_manager.py create "Folder Name"
```

### `routine_uploader.py`
**Purpose:** Upload a single routine to a specific folder
**Usage:** `python routine_uploader.py file.json --folder-title "HSF 15"`

### `scripts/batch_routine_uploader.py`
**Purpose:** Batch upload multiple routines to a folder
**Usage:** `python scripts/batch_routine_uploader.py file.json --folder-title "HSF 15"`

### `scripts/create_new_folder.py`
**Purpose:** Create a new folder with auto-incremented naming
**Usage:** `python scripts/create_new_folder.py`

## Workflow: When You Receive a New Routine

### Step 1: Check Current Folders
```bash
python scripts/get_recent_folder.py
```

### Step 2: Create New Folder
```bash
python scripts/create_new_folder.py
```

### Step 3: Upload Routines to New Folder
```bash
# Single routine
python routine_uploader.py new_routine.json --folder-title "HSF 16"

# Batch upload
python scripts/batch_routine_uploader.py extracted_routines.json --folder-title "HSF 16"
```

### Step 4: Verify in Hevy App
- Open the Hevy app
- Verify routines appear in the new folder
- Check all exercises and sets are correct

## Best Practices

### Always Verify Folder First
```bash
python scripts/get_recent_folder.py
```

### Consistent Naming
- Use format: `HSF N` (where N is incremented)
- Keep historical folders for reference

### Batch Operations
- Group related routines in the same folder
- Use `--folder-title` consistently
- Dry-run before actual upload: `--dry-run`

### Archive Strategy
- Keep previous cycles (HSF 14, 13, etc.) for history
- Reference old routines when creating new ones
- Never delete folders; just stop using them

## API Methods Reference

### In Python Code
```python
from hevy_api_client import HevyAPIClient

client = HevyAPIClient()

# List folders
folders = client.list_routine_folders(page=1, page_size=10)

# Find a specific folder
folder = client.find_routine_folder_by_title("HSF 15")

# Ensure folder exists (create if needed)
folder = client.ensure_routine_folder("HSF 15")
folder_id = folder['id']

# Create a new folder
response = client.create_routine_folder("HSF 16")
```

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Folder not found | May not have synced | Run `python scripts/get_recent_folder.py` to verify |
| Upload to wrong folder | Folder ID mismatch | Check `--folder-title` matches exactly |
| API error 400 | Page size > 10 | Use default `page_size=10` |
| Can't create folder | Duplicate name | Use a unique folder name with a number |

## When You Receive New Routines

1. Check the current folder:
   ```bash
   python scripts/get_recent_folder.py
   ```

2. Verify you're using the correct folder, usually HSF 15:
   ```bash
   python routine_uploader.py new_routine.json --folder-title "HSF 15"
   ```

3. If creating a new cycle:
   ```bash
   python scripts/create_new_folder.py
   ```

4. Upload to the new folder:
   ```bash
   python scripts/batch_routine_uploader.py extracted_routines.json --folder-title "HSF 16"
   ```