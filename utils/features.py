# ========================================
# FEATURE EXTRACTION PIPELINE
# ========================================
# This script processes raw keystroke data (CSV files) and extracts
# behavioral features for analysis. It calculates timing metrics like
# hold time, flight time, and typing speed for each session.

# === IMPORTS ===
import os                # For file system operations (paths, directories)
import pandas as pd      # For data manipulation and CSV operations
from glob import glob    # For finding files matching patterns (e.g., *.csv)
import numpy as np       # For numerical operations and NaN handling

# === DIRECTORY CONFIGURATION ===
# Where to find raw data (input) and where to save processed features (output)
RAW_DIR = "data/raw"           # Input: Raw keystroke CSV files
OUT_DIR = "data/processed"     # Output: Processed feature CSV
os.makedirs(OUT_DIR, exist_ok=True)  # Create output directory if it doesn't exist

def compute_features(df):
    """
    Calculate behavioral features from raw keystroke timing data.
    
    Takes a DataFrame with keystroke events and computes:
    - Hold time: How long keys are pressed down
    - Flight time: Pauses between consecutive keystrokes
    - Typing speed: Keys per second
    
    Args:
        df: DataFrame with columns: t_down_ms, t_up_ms, order_index
    
    Returns:
        Dictionary with calculated features (mean_hold, std_hold, etc.)
    """

    # ========================================
    # STEP 1: Sort by typing order
    # ========================================
    # Ensure keystrokes are in chronological order (first typed to last typed)
    # This is critical for calculating time differences between consecutive keys
    df = df.sort_values("order_index")

    # ========================================
    # STEP 2: Calculate HOLD TIME
    # ========================================
    # Hold time = how long a key is pressed down (release time - press time)
    # Example: If 'a' pressed at 1000ms and released at 1150ms → hold_time = 150ms
    df["hold_time"] = df["t_up_ms"] - df["t_down_ms"]

    # ========================================
    # STEP 3: Calculate FLIGHT TIME
    # ========================================
    # Flight time = pause between releasing one key and pressing the next
    # This measures the gap between consecutive keystrokes
    
    # 3a. Get the NEXT keystroke's press time using shift(-1)
    # shift(-1) moves all values up by 1 row, so each row sees the next row's value
    df["next_t_down"] = df["t_down_ms"].shift(-1)
    
    # 3b. Calculate flight time: next key press - current key release
    # Example: Released 'h' at 1150ms, pressed 'e' at 1300ms → flight_time = 150ms
    df["flight_time"] = df["next_t_down"] - df["t_up_ms"]
    
    # 3c. Remove the last row (it has no "next key" so flight_time is NaN)
    df = df.dropna(subset=["flight_time"])

    # ========================================
    # SAFETY CHECK: Minimum data requirement
    # ========================================
    # If less than 2 keystrokes, we can't calculate meaningful features
    # Return NaN (Not a Number) for all features
    if len(df) < 2:
        return {
            "mean_hold": np.nan,
            "std_hold": np.nan,
            "mean_flight": np.nan,
            "std_flight": np.nan,
            "typing_speed": np.nan
        }

    # ========================================
    # STEP 4: Calculate TYPING SPEED
    # ========================================
    # Typing speed = total keys typed ÷ total time duration
    
    # 4a. Calculate total duration: last key release - first key press
    duration_ms = df["t_up_ms"].max() - df["t_down_ms"].min()

    # 4b. Calculate keys per second (avoid division by zero)
    if duration_ms <= 0:
        typing_speed = np.nan
    else:
        # Convert milliseconds to seconds by dividing by 1000
        typing_speed = len(df) / (duration_ms / 1000)

    # ========================================
    # CLEANUP: Remove temporary columns
    # ========================================
    # Drop the helper column we created (next_t_down)
    # errors="ignore" means don't crash if column doesn't exist
    df = df.drop(columns=["next_t_down"], errors="ignore")

    # ========================================
    # STEP 5: Return aggregated features
    # ========================================
    # Calculate summary statistics for this typing session
    return {
        "mean_hold": df["hold_time"].mean(),        # Average hold time
        "std_hold": df["hold_time"].std(),          # Hold time consistency (standard deviation)
        "mean_flight": df["flight_time"].mean(),    # Average pause between keys
        "std_flight": df["flight_time"].std(),      # Flight time consistency
        "typing_speed": typing_speed                # Keys per second
    }

def main():
    """
    Main function that processes all raw CSV files and extracts features.
    
    Workflow:
    1. Find all CSV files in data/raw/
    2. For each file, load the data
    3. Extract metadata (participant ID, condition, etc.)
    4. Calculate behavioral features (hold time, flight time, typing speed)
    5. Combine features and metadata into one row
    6. Save all rows to data/processed/features.csv
    """
    
    # ========================================
    # STEP 1: Initialize storage
    # ========================================
    # This list will hold one dictionary per CSV file (one per session)
    feature_rows = []

    # ========================================
    # STEP 2: Loop through all CSV files
    # ========================================
    # glob() finds all files matching the pattern "data/raw/*.csv"
    # os.path.join() creates the path: "data/raw" + "/" + "*.csv"
    for filepath in glob(os.path.join(RAW_DIR, "*.csv")):
        print(f"Processing {filepath}...")
        
        # Load the CSV file into a pandas DataFrame (table)
        df = pd.read_csv(filepath)

        # ========================================
        # STEP 3: Extract metadata from first row
        # ========================================
        # All rows in one CSV have the same metadata, so we just grab from row 0
        # .iloc[0] means "get the value at index 0 (first row)"
        participant_id = df["participant_id"].iloc[0]  # Who typed this
        session_id = df["session_id"].iloc[0]          # Which session number
        condition = df["condition"].iloc[0]            # Morning, Fatigue, etc.
        task_type = df["task_type"].iloc[0]            # fixed or free

        # ========================================
        # STEP 4: Compute behavioral features
        # ========================================
        # Call compute_features() to calculate timing metrics
        # Returns a dictionary: {"mean_hold": 145.2, "std_hold": 23.5, ...}
        feats = compute_features(df)

        # ========================================
        # STEP 5: Add metadata to features
        # ========================================
        # Attach identifying information to the feature dictionary
        # This way we know WHO typed this and UNDER WHAT CONDITIONS
        feats["participant_id"] = participant_id
        feats["session_id"] = session_id
        feats["condition"] = condition
        feats["task_type"] = task_type
        feats["file"] = os.path.basename(filepath)  # Just the filename, not full path

        # ========================================
        # STEP 6: Add this session's features to our list
        # ========================================
        # Each dictionary represents one typing session
        feature_rows.append(feats)

    # ========================================
    # STEP 7: Convert list of dictionaries to DataFrame
    # ========================================
    # pd.DataFrame() converts:
    # [{"mean_hold": 145, ...}, {"mean_hold": 180, ...}]
    # into a nice table with rows and columns
    final_df = pd.DataFrame(feature_rows)

    # ========================================
    # STEP 8: Sort for readability
    # ========================================
    # Sort by participant ID first, then session ID
    # This groups all sessions from the same participant together
    final_df = final_df.sort_values(["participant_id", "session_id"])

    # ========================================
    # STEP 9: Save to CSV
    # ========================================
    # Create the output file path: "data/processed/features.csv"
    output_path = os.path.join(OUT_DIR, "features.csv")
    
    # Save the DataFrame to CSV without row numbers (index=False)
    final_df.to_csv(output_path, index=False)

    # ========================================
    # STEP 10: Confirm success
    # ========================================
    print(f"✅ Feature extraction complete. Saved to {output_path}")
    print(f"📊 Processed {len(feature_rows)} sessions from {len(feature_rows)} files.")

# ========================================
# SCRIPT ENTRY POINT
# ========================================
# This block runs when you execute: python utils/features.py
# It doesn't run if this file is imported as a module
if __name__ == "__main__":
    main()