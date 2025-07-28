import pandas as pd
import json
import os

RATINGS_FILE = "data/user_ratings.json"
INTERESTS_FILE = "data/user_interests.json"

def load_courses(path="data/courses.csv"):
    """Load courses CSV and ensure course_id is string."""
    if not os.path.exists(path):
        print(f"[WARN] Courses file not found: {path}")
        return pd.DataFrame(columns=["course_id", "course_name", "category"])
    
    df = pd.read_csv(path)

    # Ensure consistent column names and string IDs
    if 'course_id' in df.columns:
        df['course_id'] = df['course_id'].astype(str)
    else:
        raise ValueError("courses.csv must contain 'course_id' column")

    return df

def print_courses(df):
    """Print available courses to console (for debugging)."""
    print("\nAvailable Courses:")
    for _, row in df.iterrows():
        print(f"{row['course_id']}. {row['course_name']} ({row['category']})")

def load_json(file_path):
    """Load JSON file or return empty dict if missing."""
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r") as f:
        return json.load(f)

def save_json(data, file_path):
    """Save dictionary to JSON file (pretty-printed)."""
    # Ensure data folder exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
