# Keystroke Dynamics Data Collection Tool

This tool collects keystroke timing data for behavioral analysis research. It records key press and release times along with session metadata.

---

## 📋 Prerequisites

- **Python 3.7+** installed on your computer
- **macOS users**: You'll need to grant Accessibility permissions (instructions below)
- **Internet connection** to access MonkeyType

---

## 🚀 Setup Instructions

### 1. Clone/Download the Project

Download this project folder to your computer.

### 2. Install Dependencies

Open Terminal (macOS/Linux) or Command Prompt (Windows) and navigate to the project folder:

```bash
cd /path/to/kba
```

Create and activate a virtual environment:

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

Install required packages:
```bash
pip install -r requirements.txt
```

### 3. Grant Accessibility Permissions (macOS Only)

For the keystroke logger to work on macOS:

1. Go to **System Settings** → **Privacy & Security** → **Accessibility**
2. Click the **+** button and add **Terminal** (or your terminal app)
3. Enable the checkbox next to Terminal
4. You may need to restart Terminal after granting permissions

---

## 📝 Data Collection Protocol

### Step 1: Prepare Your Session

Before running the script, have the following information ready:

- **Participant ID**: Your USF UID (University ID number)
- **Condition**: Your current state (Morning, Post-Caffeine, Post-Lunch, or Fatigue)
- **Task Type**: 
  - `fixed` - MonkeyType with custom text
  - `free` - Free typing

**Note:** Session IDs are automatically generated! The script will count how many times you've done this specific condition and assign the next session number.

### Step 2: Open MonkeyType (DO THIS FIRST!)

⚠️ **IMPORTANT: Open MonkeyType BEFORE running the script!**

1. Go to **[MonkeyType.com](https://monkeytype.com/)**
2. Click on **"Custom"** at the top
3. Click on **"Change"** to enter custom text
4. Enter this for your typing prompt:
   ```
   The quick brown fox jumps over the lazy dog while typing steadily to complete this sentence for biometric analysis.
   ```
5. Keep this browser window/tab open and ready
6. Position your hands on the keyboard

**Only after MonkeyType is loaded and ready, proceed to Step 3.**

### Step 3: Run the Data Collector

In your terminal (with virtual environment activated), run:

```bash
python utils/collector.py
```

Answer the prompts:
```
==================================================
📊 KEYSTROKE DATA COLLECTION TOOL
==================================================

Enter Your Participant ID (USF UID): [YOUR USF UID]

Select your current state:
  1: Morning
  2: Post-Caffeine
  3: Post-Lunch
  4: Fatigue

Enter a number (1-4): 1
✓ Condition set to: Morning
➡️  Auto-assigned Session ID: 1

Enter task type (fixed/free): fixed
✓ Task type set to: fixed
```

You'll see:
```
Recording for Participant [YOUR_UID] | Condition: Morning
Press ESC when finished.
```

### Step 4: Complete the MonkeyType Test

1. **Switch to your MonkeyType browser window**
2. **Start typing the test!** The script is now recording all your keystrokes
3. **Complete the entire test**
4. **After finishing, press ESC** to stop recording and save the data

### Step 5: Verify Data Saved

### You should see:
```
✅ Saved X rows to data/raw/1234567_Morning_S1.csv
```

The CSV file will be in the `data/raw/` folder.

---

## 📁 Output Data Format

Each session generates a CSV file named: `{participant_id}_{condition}_S{session_id}.csv`

**Example:** `1234567_Morning_S1.csv` (first Morning session for participant 1234567)

**Session ID Logic:**
- Session IDs are **auto-generated per condition**
- If you do Morning twice, you'll get `Morning_S1.csv` and `Morning_S2.csv`
- Each condition has its own session counter
- This allows participants to repeat conditions if needed

### CSV Columns:
- `participant_id` - Unique participant identifier
- `session_id` - Session number
- `condition` - State during typing (Morning, Post-Caffeine, etc.)
- `task_type` - Type of task (fixed/free)
- `key_code` - Which key was pressed
- `t_down_ms` - Timestamp when key was pressed (milliseconds)
- `t_up_ms` - Timestamp when key was released (milliseconds)
- `order_index` - Order of keystroke in sequence

---

## ⚠️ Important Notes

### Before Each Session:
- ✅ **FIRST: Open MonkeyType and load the test**
- ✅ **THEN: Run the Python script**
- ✅ Close unnecessary applications
- ✅ Ensure you're in the correct condition (e.g., don't select "Post-Caffeine" if you haven't had coffee)
- ✅ Make sure your hands are positioned on the keyboard

### During Recording:
- ⚠️ **DO NOT switch applications** during the test
- ⚠️ **DO NOT press ESC** until you've finished typing
- ⚠️ If you make a mistake and press ESC early, you'll need to redo the session

### After Recording:
- ✅ Verify the CSV file was created in `data/raw/`
- ✅ Check that the file contains data (should have multiple rows)
- ✅ If the file says "No keystrokes recorded", you need to redo the session

---

## 🔧 Troubleshooting

### "No module named 'pynput'" or "No module named 'pandas'"
**Solution:** Make sure you activated the virtual environment and ran `pip install -r requirements.txt`

### macOS: Keystrokes not being recorded
**Solution:** Grant Accessibility permissions to Terminal (see Step 3 in Setup)

### "No keystrokes recorded" message
**Solution:** Make sure you actually typed something before pressing ESC

### Script not responding to input
**Solution:** 
1. Press `Ctrl+C` to stop the script
2. Restart your terminal
3. Reactivate the virtual environment
4. Try again

---

## 🔬 Data Processing & Analysis Pipeline

After collecting keystroke data, you can extract behavioral features and perform authentication analysis.

### Feature Extraction

The `features.py` script processes raw keystroke data and calculates behavioral metrics:

**Run feature extraction:**
```bash
python utils/features.py
```

**Features Calculated:**
- **Hold Time (mean & std)**: How long keys are held down
- **Flight Time (mean & std)**: Time between consecutive keystrokes
- **Typing Speed**: Keys per second

**Output:** Creates `data/processed/features.csv` with aggregated features per session.

### Authentication System

The `authentication.py` script evaluates how well keystroke patterns can distinguish between users:

**Run authentication analysis:**
```bash
python utils/authentication.py
```

**How it works:**
1. Creates user templates from Morning session data
2. Computes **genuine scores**: Distance between user and their own template
3. Computes **impostor scores**: Distance between user and other users' templates
4. Uses Euclidean distance as the similarity metric

**Output:**
- `data/processed/genuine_scores.csv` - Scores for legitimate users
- `data/processed/impostor_scores.csv` - Scores for impostors

**Note:** You need data from multiple participants to generate impostor scores!

---

## 📊 Data Collection Schedule

### Recommended Sessions per Participant:

| Session | Condition | Task Type | When |
|---------|-----------|-----------|------|
| 1 | Morning | fixed | 8-10 AM |
| 2 | Post-Caffeine | fixed | 30 min after coffee |
| 3 | Post-Lunch | fixed | 1-2 PM |
| 4 | Fatigue | fixed | 4-6 PM |

**Note:** Wait at least 2 hours between sessions for meaningful data.

---

## 👥 Team Guidelines

### Data Naming Convention:
- Use your actual USF UID as Participant ID
- Session IDs are automatically assigned based on how many times you've done each condition
- Use descriptive conditions that match your actual state
- File format: `{UID}_{Condition}_S{SessionNumber}.csv`

### Data Storage:
- All CSV files should be stored in `data/raw/`
- **DO NOT** delete or modify CSV files after collection
- Backup your data regularly

### Quality Checks:
- Each CSV should have 100+ rows (one MonkeyType test typically has 200-500 keystrokes)
- Verify timestamps are in milliseconds (13-digit numbers)
- Check that `order_index` is sequential (0, 1, 2, 3...)

---

## 📧 Questions?

If you encounter any issues during data collection, contact the project lead or create an issue in the project repository.

---

## 🎯 Quick Start Checklist

- [ ] Python and pip installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Accessibility permissions granted (macOS)
- [ ] MonkeyType website open and ready
- [ ] USF UID (Participant ID) ready
- [ ] Condition/state identified
- [ ] `data/raw/` folder exists
- [ ] Ready to type!

**Good luck with your data collection! 🚀**
