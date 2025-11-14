import pandas as pd
import numpy as np
from scipy.spatial.distance import euclidean, cityblock

FEATURES_PATH = "utils/data/processed/features.csv"

FEATURE_COLUMNS = [
    "mean_hold",
    "std_hold",
    "mean_flight",
    "std_flight",
    "typing_speed"
]

def load_features():
    df = pd.read_csv(FEATURES_PATH)
    return df

def get_user_templates(df):
    templates = {}

    for pid in df["participant_id"].unique():
        user_df = df[df["participant_id"] == pid]

        # ALL Morning Sessions for this user
        morning_df = user_df[user_df["condition"] == "Morning"]

        # Skip user if no morning sessions
        if morning_df.empty:
            continue

        # Compute the averaged templates across all morning sessions
        template_vec = morning_df[FEATURE_COLUMNS].mean()

        templates[pid] = template_vec

    return templates

def compute_scores(df, templates):
    genuine_scores = []
    impostor_scores = []

    for pid, template_vec in templates.items():
        # pid is the participant id
        # template_vec is a Series with our 5 features

        # convert template to a numpy array of floats
        template = template_vec[FEATURE_COLUMNS].values.astype(float)

        # Same User Sessions
        same_user_df = df[df["participant_id"] == pid]

        # Other Users' Sessions
        other_users_df = df[df["participant_id"] != pid]

        # Genuine Scores: Template vs Same User's Sessions
        for _, row in same_user_df.iterrows():
            session_vec = row[FEATURE_COLUMNS].values.astype(float)
            dist = euclidean(template, session_vec)
            genuine_scores.append(dist)

        # Imposter Scores: Template vs Other User's Sessions
        for _, row in other_users_df.iterrows():
            session_vec = row[FEATURE_COLUMNS].values.astype(float)
            dist = euclidean(template, session_vec)
            impostor_scores.append(dist)

    return genuine_scores, impostor_scores

def save_scores(genuine_scores, impostor_scores):
    """
    Save genuine and impostor scores to CSV files.
    
    Args:
        genuine_scores: List of distances between users and their own templates
        impostor_scores: List of distances between users and other users' templates
    """
    # Create DataFrames from the score lists
    genuine_df = pd.DataFrame({"score": genuine_scores})
    impostor_df = pd.DataFrame({"score": impostor_scores})
    
    # Save to CSV files
    genuine_df.to_csv("utils/data/processed/genuine_scores.csv", index=False)
    impostor_df.to_csv("utils/data/processed/impostor_scores.csv", index=False)

    print(f"✅ Saved {len(genuine_scores)} genuine scores and {len(impostor_scores)} impostor scores")


def main():
    df = load_features()
    templates = get_user_templates(df)

    genuine_scores, impostor_scores = compute_scores(df, templates)

    save_scores(genuine_scores, impostor_scores)

    print("Authentication Scoring Complete.")


if __name__ == "__main__":
    main()