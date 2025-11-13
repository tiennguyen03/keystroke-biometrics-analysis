import os
import pandas as pd
from glob import glob
import numpy as np

RAW_DIR = "data/raw"
OUT_DIR = "data/processed"
os.makedirs(OUT_DIR, exist_ok=True)

def compute_features(df):
    """
    Compute hold time, flight time, typing speed
    for a single typing session (one CSV).
    """

    # 1. Sort by typing order
    df = df.sort_values("order_index")

    # 2. HOLD TIME (press -> release )
    df["hold_time"] = df["t_up_ms"] - df["t_down_ms"]

    # 3. FLIGHT TIME (release -> next press)
    df["next_t_down"] = df["t_down_ms"].shift(-1)
    df["flight_time"] = df["next_t_down"] - df["t_up_ms"]
    df = df.dropna(subset=["flight_time"])

    # If too few events, return NaNs safely
    if len(df) < 2:
        return {
            "mean_hold": np.nan,
            "std_hold": np.nan,
            "mean_flight": np.nan,
            "std_flight": np.nan,
            "typing_speed": np.nan
        }

    # 4. TYPING SPEED (keys per second)
    duration_ms = df["t_up_ms"].max() - df["t_down_ms"].min()

    # Avoid division by zero
    if duration_ms <= 0:
        typing_speed = np.nan
    else:
        typing_speed = len(df) / (duration_ms / 1000)

    # Clean temporary columns
    df = df.drop(columns=["next_t_down"], errors="ignore")

    # 5. Retuen session-level summary
    return {
        "mean_hold": df["hold_time"].mean(),
        "std_hold": df["hold_time"].std(),
        "mean_flight": df["flight_time"].mean(),
        "std_flight": df["flight_time"].std(),
        "typing_speed": typing_speed
    }

def main():
    # List of Dictionaries to hold the data
    feature_rows = []

    # Loop through all CSV files
    for filepath in glob(os.path.join(RAW_DIR, "*.csv")):
        print(f"Processing {filepath}...")
        df = pd.read_csv(filepath)

        # Extract Metadata from this Session
        participant_id = df["participant_id"].iloc[0]
        session_id = df["session_id"].iloc[0]
        condition = df["condition"].iloc[0]
        task_type = df["task_type"].iloc[0]

        # Compute features for this session
        feats = compute_features(df)

        # Attach Metadata to the feature dict
        feats["participant_id"] = participant_id
        feats["session_id"] = session_id
        feats["condition"] = condition
        feats["task_type"] = task_type
        feats["file"] = os.path.basename(filepath)

        feature_rows.append(feats)

    # Convert to DataFrame & save
    final_df = pd.DataFrame(feature_rows)

    # Sort nicely for readibility
    final_df = final_df.sort_values(["participant_id", "session_id"])

    # Save to processed directory
    output_path = os.path.join(OUT_DIR, "features.csv")
    final_df.to_csv(output_path, index=False)

    print(f"✅ Feature extraction complete. Saved to {output_path}")

if __name__ == "__main__":
    main()