# Routine Folder Management Guide

## 🚀 Quick Commands

### View All Folders & Most Recent
```bash
python get_recent_folder.py
```

### Create New Folder (Auto-Incremented)
```bash
# Automatically determines next folder name and asks for confirmation
# E.g., HSF 15 → HSF 16
python create_new_folder.py
```

### Create Folder with Custom Name
```bash
python folder_manager.py create "Custom Folder Name"
```

### Upload to Specific Folder
```bash
# Single routine
python routine_uploader.py input/dia_7_espalda.json --folder-title "HSF 15"

# Batch upload
python batch_routine_uploader.py extracted_routines.json --folder-title "HSF 15"
```

### Create New Folder
```bash
python folder_manager.py create "HSF 16"
```

---

## 📋 Current Routine Folders (As of April 25, 2026)

| Rank | Name | ID | Purpose |
|------|------|----|---------| 
| 1 | **HSF 15** | 2482205 | Current (most recent) |
| 2 | HSF 14 | 2262799 | Previous cycle |
| 3 | HSF 13 | 1986567 | Archive |
| 4 | HSF 12 | 1812915 | Archive |
| 5 | HSF 11 | 1665240 | Archive |
| 6-10 | HSF 10-6 | Various | Older cycles |

---

## 🔍 Understanding Folder Structure

### Folder Index
- **Index 0**: Most recent folder (appears first in API responses)
- **Index 1-9**: Older folders in reverse chronological order
- Displayed in the `get_recent_folder.py` output

### When to Update
- When uploading new routine: Use current folder (HSF 15)
- When creating new cycle: Create new folder with next number (HSF 16)
- When organizing old routines: Use archive folders for reference

---

## 🛠 Available Scripts & Commands

### `get_recent_folder.py`
**Purpose:** Display all folders ranked by recency  
**Usage:** `python get_recent_folder.py`  
**Output:** List with most recent highlighted

### `folder_manager.py`
**Purpose:** Manage folders via CLI  
**Commands:**
```bash
# List all folders
python folder_manager.py list

# Create new folder
python folder_manager.py create "Folder Name"
```

### `routine_uploader.py`
**Purpose:** Upload single routine to specific folder  
**Usage:** `python routine_uploader.py file.json --folder-title "HSF 15"`

### `batch_routine_uploader.py`
**Purpose:** Batch upload multiple routines to folder  
**Usage:** `python batch_routine_uploader.py file.json --folder-title "HSF 15"`

### `create_new_folder.py`
**Purpose:** Create new folder with auto-incremented naming  
**Usage:** `python create_new_folder.py`  
**Output:** Proposes next folder name (e.g., HSF 15 → HSF 16), asks for confirmation, then creates

---

## 🎯 Workflow: When You Receive a New Routine

### Step 1: Check Current Folders
```bash
python get_recent_folder.py
```
Shows all folders with most recent highlighted

### Step 2: Create New Folder
```bash
python create_new_folder.py
```
**What it does:**
- Automatically determines next folder name (e.g., HSF 15 → HSF 16)
- Shows you the proposed name
- Asks for confirmation (y/n)
- Creates the folder when confirmed

**Example:**
```
📋 Current Setup:
   Next folder name: HSF 16

❓ Create new folder 'HSF 16'? (y/n): y

✅ Folder created successfully!
   Folder Name: HSF 16
   Folder ID:   2500123
```

### Step 3: Upload Routines to New Folder
```bash
# Single routine
python routine_uploader.py new_routine.json --folder-title "HSF 16"

# Batch upload
python batch_routine_uploader.py extracted_routines.json --folder-title "HSF 16"
```

### Step 4: Verify in Hevy App
- Open Hevy app
- Verify routines appear in the new folder
- Check all exercises and sets are correct

---

## 💡 Best Practices

### 1. Always Verify Folder First
```bash
# Check current folder before uploading
python get_recent_folder.py
```

### 1.5 Post-Creation Validation Output (Required)
After creating any routine, always return a summary table in chat using this exact format:

| # | Exercise | Sets x Reps | Intensity | Weight |
|---|---|---|---|---|

Include one row per exercise and keep the values aligned with the routine that was uploaded.
This table is used as the final user validation checkpoint after each routine creation.

### 2. Consistent Naming
- Use format: `HSF N` (where N is incremented)
- Keep historical folders for reference

### 3. Batch Operations
- Group related routines in same folder
- Use `--folder-title` flag consistently
- Dry-run before actual upload: `--dry-run`

### 4. Archive Strategy
- Keep previous cycles (HSF 14, 13, etc.) for history
- Reference old routines when creating new ones
- Never delete folders - just stop using them

---

## 🔗 API Methods Reference

### In Python Code
```python
from hevy_api_client import HevyAPIClient

client = HevyAPIClient()

# List folders
folders = client.list_routine_folders(page=1, page_size=10)

# Find specific folder
folder = client.find_routine_folder_by_title("HSF 15")

# Ensure folder exists (create if needed)
folder = client.ensure_routine_folder("HSF 15")
folder_id = folder['id']

# Create new folder
response = client.create_routine_folder("HSF 16")
```

---

## ⚠️ Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Folder not found | May not have synced | Run `get_recent_folder.py` to verify |
| Upload to wrong folder | Folder ID mismatch | Check `--folder-title` matches exactly |
| API error 400 | Page size > 10 | Use default page_size (10 max) |
| Can't create folder | Duplicate name | Use unique folder name with number |

---

## 📝 When You Receive New Routines

1. **Check current folder:**
   ```bash
   python get_recent_folder.py
   ```

2. **Verify you're using correct folder** (usually HSF 15):
   ```bash
   python routine_uploader.py new_routine.json --folder-title "HSF 15"
   ```

3. **Or if creating new cycle:**
   ```bash
   python folder_manager.py create "HSF 16"
   python batch_routine_uploader.py routines.json --folder-title "HSF 16"
   ```

4. **Verify in app:**
   - Open Hevy app
   - Check routines appear in correct folder
