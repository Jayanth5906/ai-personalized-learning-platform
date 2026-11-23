"""
Core Business Logic Helpers for AI-Powered Personalized Learning Platform.
Calculates subject performance, recommendation algorithms, student risk analysis, and topic metrics.
"""

import pandas as pd
from database.database import (
    execute_query, execute_single_query, query_to_dataframe
)
from ml.predictor import predict_learning_level

# --- 1. Subject Performance Calculations ---

def calculate_subject_performance(student_id):
    """
    Calculate weighted average score per subject for a specific student.
    Combines quiz results and assignment scores.
    """
    q_df = query_to_dataframe(
        "SELECT subject, score FROM quiz_results WHERE student_id = ?", (student_id,)
    )
    a_df = query_to_dataframe(
        "SELECT subject, score FROM assignments WHERE student_id = ?", (student_id,)
    )
    
    if q_df.empty and a_df.empty:
        return {}
        
    combined = pd.concat([q_df, a_df], ignore_index=True)
    if combined.empty:
        return {}
        
    perf = combined.groupby('subject')['score'].mean().round(1).to_dict()
    return perf

def identify_strong_subjects(student_id, threshold=75.0):
    """Identify subjects where student score >= threshold (default 75%)."""
    perf = calculate_subject_performance(student_id)
    return [subj for subj, score in perf.items() if score >= threshold]

def identify_average_subjects(student_id, lower=50.0, upper=74.9):
    """Identify subjects where student score is between lower and upper (default 50-74%)."""
    perf = calculate_subject_performance(student_id)
    return [subj for subj, score in perf.items() if lower <= score <= upper]

def identify_weak_subjects(student_id, threshold=50.0):
    """Identify subjects where student score < threshold (default 50%)."""
    perf = calculate_subject_performance(student_id)
    return [subj for subj, score in perf.items() if score < threshold]

# --- 2. Personalized Learning Recommendation Engine ---

def generate_recommendations(student_id):
    """
    Generate personalized learning recommendations tailored to:
    - Predicted student learning level
    - Weak subjects (< 50% score)
    - Completed resources (already completed items are strictly excluded!)
    """
    # Predict dynamic learning level
    pred_res = predict_learning_level(student_id=student_id)
    learning_level = pred_res['learning_level']
    
    # Identify weak subjects
    weak_subjects = identify_weak_subjects(student_id)
    
    # Get IDs of resources already completed by this student
    completed_rows = execute_query(
        "SELECT resource_id FROM progress WHERE student_id = ? AND completed = 1", (student_id,)
    )
    completed_ids = {row['resource_id'] for row in completed_rows}
    
    # Query all available learning resources
    all_resources = query_to_dataframe("SELECT * FROM learning_resources")
    if all_resources.empty:
        return []
        
    # Filter out completed resources
    uncompleted = all_resources[~all_resources['id'].isin(completed_ids)].copy()
    if uncompleted.empty:
        return []
        
    # Score & rank uncompleted resources for student
    # High priority: Weak subjects matching resource subject OR matching difficulty level
    recommendations = []
    
    for _, res in uncompleted.iterrows():
        score = 0
        r_subj = res['subject']
        r_diff = res['difficulty']
        
        # Rule 1: Highest boost if resource subject matches a weak subject
        if r_subj in weak_subjects:
            score += 50
            
        # Rule 2: Boost if difficulty aligns with student's learning level
        if r_diff == learning_level:
            score += 30
        elif (learning_level == 'Beginner' and r_diff == 'Intermediate') or (learning_level == 'Intermediate' and r_diff == 'Beginner'):
            score += 15
            
        # Rule 3: Practice & video resources get extra relevance for weak subjects
        if r_subj in weak_subjects and res['resource_type'] in ['Video', 'Practice Questions', 'Quiz']:
            score += 20
            
        recommendations.append({
            'id': res['id'],
            'title': res['title'],
            'subject': res['subject'],
            'topic': res['topic'],
            'difficulty': res['difficulty'],
            'resource_type': res['resource_type'],
            'description': res['description'],
            'url': res['url'],
            'relevance_score': score
        })
        
    # Sort recommendations by relevance score descending
    sorted_recs = sorted(recommendations, key=lambda x: x['relevance_score'], reverse=True)
    return sorted_recs[:6]  # Return top recommendations

# --- 3. Early Identification of Struggling Students ---

def identify_at_risk_students():
    """
    Identify students who need improvement based on:
    - Low quiz scores (< 50%)
    - High number of incorrect attempts
    - Low study time (< 8 hours)
    - Poor subject performance
    """
    students_df = query_to_dataframe("SELECT id, name, study_time FROM students")
    if students_df.empty:
        return []
        
    at_risk_list = []
    
    for _, stu in students_df.iterrows():
        sid = stu['id']
        sname = stu['name']
        study_time = float(stu['study_time'])
        
        q_df = query_to_dataframe("SELECT score, attempts, incorrect_answers FROM quiz_results WHERE student_id = ?", (sid,))
        
        if q_df.empty:
            avg_score = 0.0
            avg_attempts = 0.0
            total_incorrect = 0
        else:
            avg_score = float(q_df['score'].mean())
            avg_attempts = float(q_df['attempts'].mean())
            total_incorrect = int(q_df['incorrect_answers'].sum())
            
        weak_subs = identify_weak_subjects(sid)
        weak_subj_str = ", ".join(weak_subs) if weak_subs else "None"
        
        # Risk assessment criteria
        reasons = []
        if avg_score < 50.0:
            reasons.append("Low overall quiz score (<50%).")
        if study_time < 8.0:
            reasons.append("Insufficient study activity (<8 hrs).")
        if avg_attempts >= 3.0 or total_incorrect >= 15:
            reasons.append("High number of incorrect quiz attempts.")
        if len(weak_subs) >= 2:
            reasons.append(f"Multiple weak subjects ({weak_subj_str}).")
            
        if len(reasons) >= 1 and avg_score < 60.0:
            at_risk_list.append({
                'student_id': sid,
                'name': sname,
                'avg_score': round(avg_score, 1),
                'weak_subject': weak_subj_str if weak_subs else "General Concepts",
                'study_time': round(study_time, 1),
                'incorrect_attempts': total_incorrect,
                'avg_attempts': round(avg_attempts, 1),
                'status': 'Needs Improvement',
                'reason': " ".join(reasons)
            })
            
    return at_risk_list

# --- 4. Class Analytics & Difficult Topic Detection ---

def identify_difficult_topics():
    """
    Analyze student quiz results by topic across the entire class to pinpoint difficult topics.
    Example output: Recursion -> 70% of students struggling -> Recommendation for revision session.
    """
    df = query_to_dataframe("""
        SELECT q.subject, q.topic, q.score, q.student_id 
        FROM quiz_results q
    """)
    if df.empty:
        return []
        
    topic_summary = []
    
    grouped = df.groupby(['subject', 'topic'])
    for (subj, topic), group in grouped:
        total_students = len(group['student_id'].unique())
        struggling_students = len(group[group['score'] < 60]['student_id'].unique())
        avg_topic_score = round(float(group['score'].mean()), 1)
        
        struggle_pct = round((struggling_students / max(total_students, 1)) * 100, 1)
        
        if struggle_pct >= 40.0:
            topic_summary.append({
                'subject': subj,
                'topic': topic,
                'avg_score': avg_topic_score,
                'total_students': total_students,
                'struggling_count': struggling_students,
                'struggle_pct': struggle_pct,
                'status': 'High Difficulty' if struggle_pct >= 60 else 'Moderate Difficulty',
                'recommendation': f"Consider conducting a targeted revision session and hands-on lab on {topic}."
            })
            
    # Sort by highest struggle percentage
    return sorted(topic_summary, key=lambda x: x['struggle_pct'], reverse=True)

def calculate_class_statistics():
    """
    Calculate aggregate summary metrics for Teacher Dashboard.
    """
    students_df = query_to_dataframe("SELECT s.id, s.name, s.learning_level FROM students s")
    total_students = len(students_df)
    
    q_df = query_to_dataframe("SELECT score, student_id FROM quiz_results")
    if not q_df.empty:
        class_avg_score = round(float(q_df['score'].mean()), 1)
        student_avg = q_df.groupby('student_id')['score'].mean().reset_index()
        student_avg = student_avg.merge(students_df, left_on='student_id', right_on='id')
        top_students = student_avg.sort_values(by='score', ascending=False).head(5).to_dict('records')
    else:
        class_avg_score = 0.0
        top_students = []
        
    at_risk = identify_at_risk_students()
    difficult_topics = identify_difficult_topics()
    
    # Learning level distribution
    level_dist = students_df['learning_level'].value_counts().to_dict()
    for level in ['Beginner', 'Intermediate', 'Advanced']:
        level_dist.setdefault(level, 0)
        
    return {
        'total_students': total_students,
        'class_avg_score': class_avg_score,
        'top_students': top_students,
        'at_risk_count': len(at_risk),
        'at_risk_students': at_risk,
        'difficult_topics': difficult_topics,
        'level_distribution': level_dist
    }

# --- 5. Aggregated Student Dashboard Data Helper ---

def get_student_dashboard_data(student_id):
    """Fetch complete aggregated data bundle for Student Dashboard."""
    stu = execute_single_query("SELECT * FROM students WHERE id = ?", (student_id,))
    if not stu:
        return None
        
    pred_res = predict_learning_level(student_id=student_id)
    subject_perf = calculate_subject_performance(student_id)
    strong_subs = identify_strong_subjects(student_id)
    avg_subs = identify_average_subjects(student_id)
    weak_subs = identify_weak_subjects(student_id)
    recs = generate_recommendations(student_id)
    
    q_df = query_to_dataframe("SELECT * FROM quiz_results WHERE student_id = ? ORDER BY date ASC", (student_id,))
    a_df = query_to_dataframe("SELECT * FROM assignments WHERE student_id = ? ORDER BY date ASC", (student_id,))
    
    avg_quiz_score = round(float(q_df['score'].mean()), 1) if not q_df.empty else 0.0
    avg_assign_score = round(float(a_df['score'].mean()), 1) if not a_df.empty else 0.0
    overall_avg = round((avg_quiz_score * 0.6) + (avg_assign_score * 0.4), 1) if q_df.empty is False else avg_assign_score
    
    completed_df = query_to_dataframe("SELECT * FROM progress WHERE student_id = ? AND completed = 1", (student_id,))
    completed_count = len(completed_df)
    
    return {
        'student_id': student_id,
        'name': stu['name'],
        'learning_level': pred_res['learning_level'],
        'confidence': pred_res['confidence'],
        'probabilities': pred_res['probabilities'],
        'overall_avg': overall_avg,
        'avg_quiz_score': avg_quiz_score,
        'avg_assign_score': avg_assign_score,
        'study_time': float(stu['study_time']),
        'completed_quizzes': len(q_df),
        'completed_resources': completed_count,
        'strong_subjects': strong_subs,
        'average_subjects': avg_subs,
        'weak_subjects': weak_subs,
        'subject_performance': subject_perf,
        'recommendations': recs,
        'quiz_history': q_df,
        'assignment_history': a_df
    }
