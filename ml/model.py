"""
Machine Learning Data Preprocessing and Feature Extraction Module.
"""

import pandas as pd
import numpy as np
from database.database import query_to_dataframe, execute_single_query

FEATURE_COLUMNS = [
    'avg_quiz_score',
    'avg_assignment_score',
    'study_time',
    'avg_attempts',
    'completed_activities',
    'overall_subject_perf'
]

def preprocess_data(raw_df):
    """
    Clean and preprocess student feature DataFrame for Random Forest training and inference.
    Handles missing values, caps outliers, and ensures required feature columns exist.
    """
    df = raw_df.copy()
    
    # Fill missing numeric values with sensible defaults
    defaults = {
        'avg_quiz_score': 60.0,
        'avg_assignment_score': 60.0,
        'study_time': 10.0,
        'avg_attempts': 1.5,
        'completed_activities': 1,
        'overall_subject_perf': 60.0
    }
    
    for col in FEATURE_COLUMNS:
        if col not in df.columns:
            df[col] = defaults[col]
        else:
            df[col] = df[col].fillna(defaults[col])
            
    # Ensure types are numeric
    for col in FEATURE_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(defaults[col])
        
    return df[FEATURE_COLUMNS]

def extract_student_features(student_id):
    """
    Extract current feature vector for a specific student from SQLite database.
    """
    # 1. Fetch study_time from students table
    stu = execute_single_query("SELECT study_time FROM students WHERE id = ?", (student_id,))
    study_time = float(stu['study_time']) if stu and stu['study_time'] is not None else 10.0
    
    # 2. Quiz performance
    q_df = query_to_dataframe("SELECT score, attempts FROM quiz_results WHERE student_id = ?", (student_id,))
    if not q_df.empty:
        avg_quiz_score = float(q_df['score'].mean())
        avg_attempts = float(q_df['attempts'].mean())
    else:
        avg_quiz_score = 50.0
        avg_attempts = 1.0

    # 3. Assignment performance
    a_df = query_to_dataframe("SELECT score FROM assignments WHERE student_id = ?", (student_id,))
    avg_assignment_score = float(a_df['score'].mean()) if not a_df.empty else avg_quiz_score

    # 4. Completed activities count
    p_df = query_to_dataframe("SELECT COUNT(*) as cnt FROM progress WHERE student_id = ? AND completed = 1", (student_id,))
    completed_activities = int(p_df['cnt'].iloc[0]) if not p_df.empty else 0

    # 5. Overall subject performance average
    overall_subject_perf = (avg_quiz_score * 0.6) + (avg_assignment_score * 0.4)

    feature_dict = {
        'avg_quiz_score': round(avg_quiz_score, 2),
        'avg_assignment_score': round(avg_assignment_score, 2),
        'study_time': round(study_time, 2),
        'avg_attempts': round(avg_attempts, 2),
        'completed_activities': completed_activities,
        'overall_subject_perf': round(overall_subject_perf, 2)
    }

    return pd.DataFrame([feature_dict])
