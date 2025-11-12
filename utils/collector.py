from pynput import keyboard
import pandas as pd
import time
import os

# Session Metadata
print("=" * 50)
print("📊 KEYSTROKE DATA COLLECTION TOOL")
print("=" * 50)
print()

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
raw_dir = "data/raw"
os.makedirs(raw_dir, exist_ok=True)

# Condition Selection
conditions = ["Morning", "Post-Caffeine", "Post-Lunch", "Fatigue"]

print("\nSelect your current state:")
for i, c in enumerate(conditions, start=1):
    print(f"  {i}: {c}")

while True:
    try:
        user_state = int(input(f"\nEnter a number (1-{len(conditions)}): "))
        if 1 <= user_state <= len(conditions):
            condition = conditions[user_state - 1]
            print(f"✓ Condition set to: {condition}")
            break
        else:
            print(f"❌ Please enter a number between 1 and {len(conditions)}.")
    except ValueError:
        print("❌ Invalid input. Please enter a valid number.")

# --- Auto-generate session ID based on participant + condition ---
existing_sessions = [
    f for f in os.listdir(raw_dir)
    if f.startswith(f"{participant_id}_{condition}_S") and f.endswith(".csv")
]

session_id = len(existing_sessions) + 1
print(f"➡️  Auto-assigned Session ID: {session_id}")

# Task Type Selection
while True:
    task_type = input("\nEnter task type (fixed/free): ").strip().lower()
    if task_type in ["fixed", "free"]:
        print(f"✓ Task type set to: {task_type}")
        break
    print("❌ Invalid input. Please enter 'fixed' or 'free'.")

# Storage Structures
press_times = {} # Temporarily Holds t_press_ms
keystrokes = [] # List of Dictionaries to Store Keystroke Data
order_index = 0

def on_press(key):
    t_press_ms = int(time.time() * 1000)
    press_times[key] = t_press_ms


def on_release(key):
    global order_index
    t_release_ms = int(time.time() * 1000)
    t_press_ms = press_times.pop(key, None) # get and remove

    if t_press_ms:
        keystrokes.append({
            "participant_id": participant_id,
            "session_id": session_id,
            "condition": condition,
            "task_type": task_type,
            "key_code": str(key),
            "t_down_ms": t_press_ms,
            "t_up_ms": t_release_ms,
            "order_index": order_index
        })
        order_index += 1

        # Show progress in console
        print(f"Recorded {len(keystrokes)} keystrokes", end='\r')

    if key == keyboard.Key.esc:
        print("\nSession ended. Saving data...")
        return False

def save_data():  
    os.makedirs("data/raw", exist_ok=True)

    # ✅ SAFETY CHECK
    if len(keystrokes) == 0:
        print("⚠️  No keystrokes recorded. File not saved.")
        print("💡 Tip: Press ESC only after typing some keystrokes.")
        return
    
    filename = f"{participant_id}_{condition}_S{session_id}.csv"
    filepath = os.path.join("data/raw", filename)

    df = pd.DataFrame(keystrokes)
    df.to_csv(filepath, index=False)
    print(f"\n✅ Saved {len(keystrokes)} rows to {filepath}")

print(f"\nRecording for Participant {participant_id} | Condition: {condition}")
print("Press ESC when finished.\n")

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

save_data()

