# ========================================
# KEYSTROKE DATA COLLECTION TOOL
# ========================================
# This script captures keyboard input timing data for behavioral analysis.
# It records when keys are pressed and released, along with metadata about
# the typing session (participant, condition, task type).

# === IMPORTS ===
from pynput import keyboard  # Library to capture keyboard events (press/release)
import pandas as pd          # For creating and saving DataFrames (tables) to CSV
import time                  # To get current timestamp in milliseconds
import os                    # For file system operations (creating directories, paths)

# ========================================
# WELCOME MESSAGE
# ========================================
# Print a header to make the tool look professional
print("=" * 50)
print("📊 KEYSTROKE DATA COLLECTION TOOL")
print("=" * 50)
print()

# ========================================
# STEP 1: COLLECT PARTICIPANT ID
# ========================================
# Ask user for their USF student ID with validation
# Loop until we get a valid positive number

while True:
    try:
        # Prompt user for their university ID
        participant_id = int(input("Enter Your Participant ID (USF UID): "))
        
        # Validate: ID must be positive
        if participant_id <= 0:
            print("❌ Participant ID must be a positive number.")
            continue  # Go back to start of loop
        
        # Valid ID entered, exit loop
        break
    except ValueError:
        # User entered something that's not a number
        print("❌ Invalid input. Please enter a valid number.")

# ========================================
# STEP 2: CREATE DATA DIRECTORY & SELECT CONDITION
# ========================================
# Create data directory if it doesn't exist
# exist_ok=True means don't crash if folder already exists
raw_dir = "data/raw"
os.makedirs(raw_dir, exist_ok=True)

# ========================================
# STEP 3: CONDITION SELECTION
# ========================================
# List of possible conditions (states) for the participant
conditions = ["Morning", "Post-Caffeine", "Post-Lunch", "Fatigue"]

# Display numbered menu of conditions
print("\nSelect your current state:")
for i, c in enumerate(conditions, start=1):
    print(f"  {i}: {c}")

# Loop until valid condition is selected
while True:
    try:
        user_state = int(input(f"\nEnter a number (1-{len(conditions)}): "))
        
        # Check if number is in valid range (1-4)
        if 1 <= user_state <= len(conditions):
            # Convert user's choice (1-4) to list index (0-3)
            condition = conditions[user_state - 1]
            print(f"✓ Condition set to: {condition}")
            break
        else:
            print(f"❌ Please enter a number between 1 and {len(conditions)}.")
    except ValueError:
        # User entered something that's not a number
        print("❌ Invalid input. Please enter a valid number.")

# ========================================
# STEP 4: AUTO-GENERATE SESSION ID
# ========================================
# Count how many sessions this participant has already done for this condition
# Example: If 2 "Morning" files exist, this will be session 3
existing_sessions = [
    f for f in os.listdir(raw_dir)
    if f.startswith(f"{participant_id}_{condition}_S") and f.endswith(".csv")
]

# Session ID = number of existing sessions + 1
session_id = len(existing_sessions) + 1
print(f"➡️  Auto-assigned Session ID: {session_id}")

# ========================================
# STEP 5: TASK TYPE SELECTION
# ========================================
# Ask user whether they're doing fixed text (TypeRacer) or free typing
while True:
    task_type = input("\nEnter task type (fixed/free): ").strip().lower()
    if task_type in ["fixed", "free"]:
        print(f"✓ Task type set to: {task_type}")
        break
    print("❌ Invalid input. Please enter 'fixed' or 'free'.")

# ========================================
# STEP 6: INITIALIZE DATA STORAGE
# ========================================
# Storage Structures:
press_times = {}  # Temporarily holds press time for each key (while key is down)
keystrokes = []   # List of dictionaries - each dict is one complete keystroke event
order_index = 0   # Counter to track the order keys were pressed

# ========================================
# STEP 7: DEFINE EVENT HANDLERS
# ========================================

def on_press(key):
    """
    Called automatically when ANY key is pressed down.
    Records the timestamp when the key was pressed.
    
    Args:
        key: The key object from pynput (e.g., 'a', Key.space, Key.enter)
    """
    # Get current time in milliseconds since epoch
    # int(time.time() * 1000) converts seconds to milliseconds
    t_press_ms = int(time.time() * 1000)
    
    # Store this timestamp temporarily (until key is released)
    # Key: the key object, Value: press timestamp
    press_times[key] = t_press_ms


def on_release(key):
    """
    Called automatically when ANY key is released.
    Records the release timestamp and saves the complete keystroke event.
    
    Args:
        key: The key object from pynput (e.g., 'a', Key.space, Key.enter)
    
    Returns:
        False if ESC is pressed (stops the listener), None otherwise
    """
    global order_index  # Need to modify the global counter variable
    
    # Get current time in milliseconds
    t_release_ms = int(time.time() * 1000)
    
    # Get and remove the press time for this key from our temporary storage
    # .pop() returns the value and removes it from the dictionary
    # Second argument (None) is returned if key not found (safety check)
    t_press_ms = press_times.pop(key, None)

    # Only process if we have a valid press time
    # (Sometimes release happens without press being recorded)
    if t_press_ms:
        # Create a dictionary with all data for this keystroke
        keystrokes.append({
            "participant_id": participant_id,
            "session_id": session_id,
            "condition": condition,
            "task_type": task_type,
            "key_code": str(key),           # Convert key object to string
            "t_down_ms": t_press_ms,        # When key was pressed
            "t_up_ms": t_release_ms,        # When key was released
            "order_index": order_index      # Sequence number (0, 1, 2, ...)
        })
        
        # Increment the counter for next keystroke
        order_index += 1

        # Show progress in console (overwrites same line with '\r')
        print(f"Recorded {len(keystrokes)} keystrokes", end='\r')

    # Check if ESC key was pressed
    if key == keyboard.Key.esc:
        print("\nSession ended. Saving data...")
        return False  # Returning False stops the keyboard listener

# ========================================
# STEP 8: DEFINE SAVE FUNCTION
# ========================================

def save_data():
    """
    Saves recorded keystroke data to a CSV file.
    
    Creates the filename based on participant ID, condition, and session ID.
    Only saves if keystrokes were actually recorded.
    """
    # Make sure output directory exists (redundant but safe)
    os.makedirs("data/raw", exist_ok=True)

    # ========================================
    # SAFETY CHECK: Verify data was collected
    # ========================================
    # If user pressed ESC immediately without typing, don't save empty file
    if len(keystrokes) == 0:
        print("⚠️  No keystrokes recorded. File not saved.")
        print("💡 Tip: Press ESC only after typing some keystrokes.")
        return  # Exit function without saving
    
    # ========================================
    # CREATE FILENAME & SAVE
    # ========================================
    # Format: {participant_id}_{condition}_S{session_id}.csv
    # Example: 1234567_Morning_S1.csv
    filename = f"{participant_id}_{condition}_S{session_id}.csv"
    filepath = os.path.join("data/raw", filename)

    # Convert list of dictionaries to pandas DataFrame (table)
    df = pd.DataFrame(keystrokes)
    
    # Save to CSV without row numbers (index=False)
    df.to_csv(filepath, index=False)
    
    # Confirm success to user
    print(f"\n✅ Saved {len(keystrokes)} rows to {filepath}")

# ========================================
# STEP 9: START RECORDING
# ========================================
# Print instructions to the user
print(f"\n✨ Recording for Participant {participant_id} | Condition: {condition}")
print("👉 Start typing in TypeRacer or any text editor")
print("👉 Press ESC when you're finished typing\n")

# ========================================
# STEP 10: START KEYBOARD LISTENER
# ========================================
# Create and start the pynput keyboard listener
# This runs in the background and calls on_press/on_release for each keystroke
# listener.join() blocks until the listener stops (when ESC is pressed)
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

# ========================================
# STEP 11: SAVE DATA AFTER RECORDING ENDS
# ========================================
# This runs after ESC is pressed and the listener stops
save_data()

