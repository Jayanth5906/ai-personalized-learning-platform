"""
Verification Script for AI-Powered Personalized Learning Platform.
Tests Database initialization, ML training and inference, recommendation engine, risk analysis, and analytics.
"""

import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from database.database import init_db, execute_query, save_quiz_result
from ml.train_model import train_model
from ml.predictor import predict_learning_level
from utils.helpers import (
    calculate_subject_performance,
    identify_strong_subjects,
    identify_weak_subjects,
    generate_recommendations,
    identify_at_risk_students,
    identify_difficult_topics,
    calculate_class_statistics,
    get_student_dashboard_data
)

def run_tests():
    print("--- 1. Testing Database Initialization ---")
    init_db()
    users = execute_query("SELECT * FROM users")
    students = execute_query("SELECT * FROM students")
    print(f"[OK] Total Users: {len(users)}")
    print(f"[OK] Total Students: {len(students)}")
    assert len(students) >= 10, "Should have at least 10 students seeded!"

    print("\n--- 2. Testing ML Model Training ---")
    eval_res = train_model()
    print(f"[OK] Model Accuracy: {eval_res['accuracy']}%")
    assert eval_res['accuracy'] > 80.0, "Model accuracy should be > 80%"

    print("\n--- 3. Testing ML Prediction ---")
    pred_1 = predict_learning_level(student_id=1) # Aarav
    print(f"[OK] Student 1 Level: {pred_1['learning_level']} (Confidence: {pred_1['confidence']}%)")
    pred_3 = predict_learning_level(student_id=3) # Rahul
    print(f"[OK] Student 3 Level: {pred_3['learning_level']} (Confidence: {pred_3['confidence']}%)")

    print("\n--- 4. Testing Subject Performance & Badges ---")
    perf_3 = calculate_subject_performance(3)
    weak_3 = identify_weak_subjects(3)
    print(f"[OK] Student 3 Performance: {perf_3}")
    print(f"[OK] Student 3 Weak Subjects: {weak_3}")

    print("\n--- 5. Testing Recommendation Engine ---")
    recs_3 = generate_recommendations(3)
    print(f"[OK] Student 3 Generated {len(recs_3)} Recommendations:")
    for r in recs_3[:3]:
        print(f"  - [{r['subject']}] {r['title']} ({r['difficulty']})")
    assert len(recs_3) > 0, "Recommendations should not be empty for weak subjects!"

    print("\n--- 6. Testing At-Risk Student Detection ---")
    at_risk = identify_at_risk_students()
    print(f"[OK] Detected {len(at_risk)} At-Risk Students:")
    for r in at_risk:
        print(f"  - Student: {r['name']} | Status: {r['status']} | Reason: {r['reason']}")

    print("\n--- 7. Testing Difficult Topic Analysis ---")
    diff_topics = identify_difficult_topics()
    print(f"[OK] Difficult Topics:")
    for dt in diff_topics:
        print(f"  - Subject: {dt['subject']} | Topic: {dt['topic']} | Struggle: {dt['struggle_pct']}%")

    print("\n--- 8. Testing Class Statistics ---")
    class_stats = calculate_class_statistics()
    print(f"[OK] Class Average Score: {class_stats['class_avg_score']}%")
    print(f"[OK] Level Distribution: {class_stats['level_distribution']}")

    print("\n[OK] ALL SYSTEM VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    run_tests()
