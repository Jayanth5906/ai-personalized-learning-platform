"""
Teacher Student Details UI Component.
Allows teachers to inspect individual student profiles, quiz history, weak subjects, recommendations, and risk status.
"""

import streamlit as st
import pandas as pd
from database.database import query_to_dataframe
from utils.helpers import get_student_dashboard_data, identify_at_risk_students
from components.ui import render_page_header

def render_student_details_page():
    """Render Student Details page for Teacher view."""
    render_page_header(
        "TEACHER WORKSPACE",
        "Student progress review",
        "Review an individual learner's performance, strengths, focus areas, and recommended support.",
        "👤",
    )

    # 1. Fetch list of all students for selection dropdown
    students_df = query_to_dataframe("SELECT id, name FROM students ORDER BY name ASC")
    if students_df.empty:
        st.warning("No students registered in database.")
        return

    student_options = dict(zip(students_df['id'], students_df['name']))
    selected_id = st.selectbox("Select Student to Inspect", options=list(student_options.keys()), format_func=lambda x: student_options[x])

    if not selected_id:
        return

    data = get_student_dashboard_data(selected_id)
    if not data:
        st.error("Failed to load student details.")
        return

    # Check if student is flagged at-risk
    at_risk_students = identify_at_risk_students()
    risk_info = next((r for r in at_risk_students if r['student_id'] == selected_id), None)

    # Header Card
    st.markdown(f"""
        <div style="background: white; border: 1px solid #E2E8F0; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h2 style="margin:0; color:#1E293B;">{data['name']}</h2>
                    <p style="margin:4px 0 0 0; color:#64748B;">Student ID: #{data['student_id']}</p>
                </div>
                <div>
                    <span style="background: #DBEAFE; color: #1E40AF; padding: 6px 14px; border-radius: 16px; font-weight: 700; font-size: 14px;">{data['learning_level']} Level</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Risk Warning Banner if At Risk
    if risk_info:
        st.markdown(f"""
            <div style="background: #FEF2F2; border: 1px solid #FCA5A5; border-left: 5px solid #EF4444; border-radius: 8px; padding: 14px; margin-bottom: 20px;">
                <h4 style="margin:0; color:#991B1B;">⚠️ At-Risk Warning: {risk_info['status']}</h4>
                <p style="margin:4px 0 0 0; color:#7F1D1D; font-size:14px;"><strong>Reason:</strong> {risk_info['reason']}</p>
            </div>
        """, unsafe_allow_html=True)

    # Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Overall Average", f"{data['overall_avg']}%")
    with m2:
        st.metric("Quiz Average", f"{data['avg_quiz_score']}%")
    with m3:
        st.metric("Study Time", f"{data['study_time']} hrs")
    with m4:
        st.metric("Completed Quizzes", data['completed_quizzes'])

    st.markdown("---")

    # Subject Breakdown
    st.subheader("🎯 Subject Proficiency Breakdown")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("**Strong Subjects (≥75%):**")
        if data['strong_subjects']:
            for s in data['strong_subjects']:
                st.success(f"{s} ({data['subject_performance'].get(s)}%)")
        else:
            st.write("None")

    with c2:
        st.markdown("**Average Subjects (50–74%):**")
        if data['average_subjects']:
            for s in data['average_subjects']:
                st.info(f"{s} ({data['subject_performance'].get(s)}%)")
        else:
            st.write("None")

    with c3:
        st.markdown("**Weak Subjects (<50%):**")
        if data['weak_subjects']:
            for s in data['weak_subjects']:
                st.error(f"{s} ({data['subject_performance'].get(s)}%)")
        else:
            st.write("None")

    st.markdown("---")

    # Quiz History & Recommendations
    t1, t2 = st.tabs(["📋 Quiz History", "💡 Current Recommendations"])

    with t1:
        q_hist = data['quiz_history']
        if not q_hist.empty:
            st.dataframe(q_hist[['date', 'subject', 'topic', 'score', 'correct_answers', 'incorrect_answers', 'attempts']], width="stretch")
        else:
            st.info("No quiz history.")

    with t2:
        recs = data['recommendations']
        if recs:
            for r in recs:
                st.markdown(f"""
                    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 12px; border-radius: 6px; margin-bottom: 8px;">
                        <strong>{r['title']}</strong> ({r['subject']} - {r['difficulty']})<br>
                        <span style="font-size: 13px; color: #64748B;">{r['description']}</span>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No active recommendations.")
