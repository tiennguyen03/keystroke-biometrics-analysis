"""
Keystroke Data Collection Tool
================================
This script collects keystroke timing data for behavioral analysis research.
It records key press and release timestamps along with session metadata.

Dependencies:
    - pynput: Captures keyboard events
    - pandas: Organizes and saves data to CSV
    - time: Provides millisecond timestamps
    - os: Handles file system operations

Output:
    CSV files in data/raw/ with format: {participant_id}_{condition}_S{session_id}.csv
"""

from pynput import keyboard
import pandas as pd
import time
import os

# ============================================================================
# SECTION 1: SESSION METADATA COLLECTION
# ============================================================================

# Display welcome header
print("=" * 50)
print("📊 KEYSTROKE DATA COLLECTION TOOL")
print("=" * 50)
print()

# Collect Participant ID (USF UID)
# Loop until valid positive integer is entered
while True:
    try:
        participant_id = int(input("Enter Your Participant ID (USF UID): "))
        if participant_id <= 0:
            print("❌ Participant ID must be a positive number.")
            continue
        break
    except ValueError:
        print("❌ Invalid input. Please enter a valid number.")

# Create data directory if it doesn't exist
# This ensures the output folder is available before checking for existing sessions
raw_dir = "data/raw"
os.makedirs(raw_dir, exist_ok=True)

# ============================================================================
# SECTION 2: CONDITION SELECTION
# ============================================================================

# Define available conditions (modify this list to add/remove conditions)
conditions = ["Morning", "Post-Caffeine", "Post-Lunch", "Fatigue"]

print("\nSelect your current state:")
for i, c in enumerate(conditions, start=1):
    print(f"  {i}: {c}")

# Loop until valid condition number is entered
while True:
    try:
        user_state = int(input(f"\nEnter a number (1-{len(conditions)}): "))
        if 1 <= user_state <= len(conditions):
            condition = conditions[user_state - 1]  # Convert to 0-based index
            print(f"✓ Condition set to: {condition}")
            break
        else:
            print(f"❌ Please enter a number between 1 and {len(conditions)}.")
    except ValueError:
        print("❌ Invalid input. Please enter a valid number.")

# ============================================================================
# SECTION 3: AUTO-GENERATE SESSION ID
# ============================================================================

# Count existing CSV files for this participant + condition combination
# This allows participants to repeat the same condition multiple times
# Example: If 2 Morning sessions exist, this will be Session 3
existing_sessions = [
    f for f in os.listdir(raw_dir)
    if f.startswith(f"{participant_id}_{condition}_S") and f.endswith(".csv")
]

session_id = len(existing_sessions) + 1
print(f"➡️  Auto-assigned Session ID: {session_id}")

# ============================================================================
# SECTION 4: TASK TYPE SELECTION
# ============================================================================

# Task type determines the typing scenario (modify options as needed)
while True:
    task_type = input("\nEnter task type (fixed/free): ").strip().lower()
    if task_type in ["fixed", "free"]:
        print(f"✓ Task type set to: {task_type}")
        break
    print("❌ Invalid input. Please enter 'fixed' or 'free'.")

# ============================================================================
# SECTION 5: DATA STRUCTURES & KEYSTROKE TRACKING
# ============================================================================

# Storage Structures:
# - press_times: Temporary dict to hold press timestamps (key -> timestamp)
# - keystrokes: List of dicts, each representing one complete keystroke
# - order_index: Sequential counter for keystroke ordering
press_times = {}
keystrokes = []
order_index = 0

def on_press(key):
    """
    Called automatically when any key is pressed down.
    
    Args:
        key: The keyboard key object from pynput
        
    Records the current timestamp in milliseconds and stores it temporarily
    in press_times dict using the key as the dictionary key.
    """
    t_press_ms = int(time.time() * 1000)  # Get current time in milliseconds
    press_times[key] = t_press_ms  # Store press time temporarily


def on_release(key):
    """
    Called automatically when any key is released.
    
    Args:
        key: The keyboard key object from pynput
        
    Returns:
        False if ESC is pressed (stops the listener), None otherwise
        
    This function:
    1. Records the release timestamp
    2. Retrieves the corresponding press timestamp
    3. Creates a complete keystroke record
    4. Appends it to the keystrokes list
    5. Increments the order counter
    6. Checks if ESC was pressed to end the session
    """
    global order_index  # Need to modify the global counter
    
    t_release_ms = int(time.time() * 1000)  # Get current time in milliseconds
    t_press_ms = press_times.pop(key, None)  # Get and remove press time from dict

    # Only record if we have a matching press event
    if t_press_ms:
        # Create a dictionary with all keystroke data
        keystrokes.append({
            "participant_id": participant_id,
            "session_id": session_id,
            "condition": condition,
            "task_type": task_type,
            "key_code": str(key),  # Convert key object to string
            "t_down_ms": t_press_ms,  # Time when key was pressed
            "t_up_ms": t_release_ms,  # Time when key was released
            "order_index": order_index  # Sequential order of keystroke
        })
        order_index += 1

        # Show progress in console (overwrites same line with \r)
        print(f"Recorded {len(keystrokes)} keystrokes", end='\r')

    # Check if ESC key was pressed
    if key == keyboard.Key.esc:
        print("\nSession ended. Saving data...")
        return False  # Returning False stops the keyboard listener

# ============================================================================
# SECTION 6: DATA SAVING FUNCTION
# ============================================================================

def save_data():
    """
    Saves keystroke data to a CSV file.
    
    Creates the output directory if it doesn't exist, validates that data was
    collected, and saves to a CSV file with a standardized naming convention.
    
    File naming format: {participant_id}_{condition}_S{session_id}.csv
    Example: 1234567_Morning_S1.csv
    """  
    os.makedirs("data/raw", exist_ok=True)

    # Safety check: Don't create empty files
    if len(keystrokes) == 0:
        print("⚠️  No keystrokes recorded. File not saved.")
        print("💡 Tip: Press ESC only after typing some keystrokes.")
        return
    
    # Construct filename with participant ID, condition, and session number
    filename = f"{participant_id}_{condition}_S{session_id}.csv"
    filepath = os.path.join("data/raw", filename)

    # Convert list of dictionaries to DataFrame and save as CSV
    df = pd.DataFrame(keystrokes)
    df.to_csv(filepath, index=False)
    print(f"\n✅ Saved {len(keystrokes)} rows to {filepath}")

# ============================================================================
# SECTION 7: START KEYBOARD LISTENER
# ============================================================================

# Display instructions to user
print(f"\nRecording for Participant {participant_id} | Condition: {condition}")
print("Press ESC when finished.\n")

# Start listening to keyboard events
# The listener will call on_press() and on_release() for each keystroke
# listener.join() blocks execution until the listener stops (when ESC is pressed)
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

# After listener stops, save the collected data
save_data()

