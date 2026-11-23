"""
Prediction Engine for Student Learning Level Classification.
"""

import os
import joblib
import pandas as pd
from ml.model import extract_student_features, preprocess_data
from ml.train_model import MODEL_PATH, train_model
from database.database import execute_update

def load_or_train_model():
    """Load pre-trained Random Forest model or train a new one if missing."""
    if not os.path.exists(MODEL_PATH):
        results = train_model()
        return results['model']
    try:
        return joblib.load(MODEL_PATH)
    except Exception:
        results = train_model()
        return results['model']

def predict_learning_level(student_id=None, feature_df=None):
    """
    Predict the learning level for a student using trained Random Forest model.
    Accepts either student_id or raw feature DataFrame.
    """
    model = load_or_train_model()
    
    if student_id is not None:
        input_features = extract_student_features(student_id)
    elif feature_df is not None:
        input_features = feature_df
    else:
        raise ValueError("Either student_id or feature_df must be provided.")
        
    X_processed = preprocess_data(input_features)
    
    prediction = model.predict(X_processed)[0]
    probabilities = model.predict_proba(X_processed)[0]
    
    # Map probabilities to class labels
    class_probs = dict(zip(model.classes_, [round(p * 100, 1) for p in probabilities]))
    confidence = class_probs.get(prediction, 0.0)
    
    # Update predicted level in database if student_id provided
    if student_id is not None:
        execute_update("UPDATE students SET learning_level = ? WHERE id = ?", (prediction, student_id))
        
    return {
        'learning_level': prediction,
        'confidence': confidence,
        'probabilities': class_probs,
        'features': X_processed.iloc[0].to_dict()
    }
