"""
Model Training Pipeline for Random Forest Student Classifier.
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from ml.model import FEATURE_COLUMNS, preprocess_data

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "student_classifier.pkl")

def generate_synthetic_training_data(n_samples=300):
    """
    Generate synthetic student performance dataset grounded in educational heuristics
    to train a robust Random Forest Classifier.
    """
    np.random.seed(42)
    
    avg_quiz_scores = np.random.uniform(30, 98, n_samples)
    avg_assignment_scores = avg_quiz_scores + np.random.normal(0, 5, n_samples)
    avg_assignment_scores = np.clip(avg_assignment_scores, 30, 100)
    
    # Study time correlates with score
    study_times = (avg_quiz_scores / 4.0) + np.random.uniform(1, 10, n_samples)
    study_times = np.clip(study_times, 2, 40)
    
    # Attempts inversely correlate with score
    avg_attempts = 4.0 - (avg_quiz_scores / 30.0) + np.random.uniform(0.1, 1.5, n_samples)
    avg_attempts = np.clip(avg_attempts, 1.0, 6.0)
    
    # Completed activities correlate with study time & score
    completed_activities = (avg_quiz_scores / 15.0) + np.random.randint(0, 5, n_samples)
    completed_activities = np.clip(completed_activities, 0, 12).astype(int)
    
    overall_subject_perf = (avg_quiz_scores * 0.6) + (avg_assignment_scores * 0.4)
    
    # Label logic based on prompt requirements:
    # Beginner: Low performance (<55%) or low study time/high attempts
    # Intermediate: Moderate performance (55% - 78%)
    # Advanced: High performance (>78%) and consistent progress
    labels = []
    for q, a, st, att, act, ov in zip(avg_quiz_scores, avg_assignment_scores, study_times, avg_attempts, completed_activities, overall_subject_perf):
        if ov < 55 or st < 8 or att > 3.5:
            labels.append('Beginner')
        elif ov > 78 and st >= 14 and att <= 2.0:
            labels.append('Advanced')
        else:
            labels.append('Intermediate')
            
    df = pd.DataFrame({
        'avg_quiz_score': avg_quiz_scores,
        'avg_assignment_score': avg_assignment_scores,
        'study_time': study_times,
        'avg_attempts': avg_attempts,
        'completed_activities': completed_activities,
        'overall_subject_perf': overall_subject_perf,
        'learning_level': labels
    })
    
    return df

def train_model():
    """
    Train Random Forest Classifier, evaluate metrics, and save model binary.
    Returns evaluation dictionary.
    """
    df = generate_synthetic_training_data(n_samples=400)
    
    X = preprocess_data(df)
    y = df['learning_level']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        random_state=42,
        class_weight='balanced'
    )
    
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    conf_matrix = confusion_matrix(y_test, y_pred, labels=['Beginner', 'Intermediate', 'Advanced'])
    
    # Ensure models directory exists
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    
    return {
        'model': model,
        'accuracy': round(acc * 100, 2),
        'classification_report': report,
        'confusion_matrix': conf_matrix,
        'feature_importances': dict(zip(FEATURE_COLUMNS, [round(val, 4) for val in model.feature_importances_]))
    }

if __name__ == '__main__':
    results = train_model()
    print(f"Model trained successfully!")
    print(f"Accuracy: {results['accuracy']}%")
    print("Feature Importances:", results['feature_importances'])
