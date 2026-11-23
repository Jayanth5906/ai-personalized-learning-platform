"""
Teacher Dashboard UI Component.
Provides class-level statistics, learning level distribution, at-risk student flags, and difficult topic insights.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.helpers import calculate_class_statistics
from database.database import query_to_dataframe
from components.ui import render_page_header

def render_teacher_dashboard():
    """Render complete interactive Teacher Dashboard."""
    stats = calculate_class_statistics()

    render_page_header(
        "TEACHER WORKSPACE",
        "Class overview",
        "Monitor learning progress, identify students who need support, and spot topics to revisit.",
        "🏫",
    )

    # 1. Top Summary Metric Cards
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown(f"""
            <div style="background: white; border: 1px solid #E2E8F0; padding: 18px; border-radius: 10px; border-left: 5px solid #6366F1;">
                <p style="margin:0; font-size: 13px; color: #64748B; font-weight: 600; text-transform: uppercase;">Total Enrolled Students</p>
                <h2 style="margin: 6px 0 0 0; font-size: 26px; font-weight: 700; color: #1E293B;">{stats['total_students']}</h2>
                <p style="margin:4px 0 0 0; font-size: 12px; color: #6366F1;">Active Cohort</p>
            </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
            <div style="background: white; border: 1px solid #E2E8F0; padding: 18px; border-radius: 10px; border-left: 5px solid #10B981;">
                <p style="margin:0; font-size: 13px; color: #64748B; font-weight: 600; text-transform: uppercase;">Class Average Score</p>
                <h2 style="margin: 6px 0 0 0; font-size: 26px; font-weight: 700; color: #1E293B;">{stats['class_avg_score']}%</h2>
                <p style="margin:4px 0 0 0; font-size: 12px; color: #10B981;">Across All Quizzes</p>
            </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
            <div style="background: white; border: 1px solid #E2E8F0; padding: 18px; border-radius: 10px; border-left: 5px solid #EF4444;">
                <p style="margin:0; font-size: 13px; color: #64748B; font-weight: 600; text-transform: uppercase;">At-Risk Students</p>
                <h2 style="margin: 6px 0 0 0; font-size: 26px; font-weight: 700; color: #EF4444;">{stats['at_risk_count']}</h2>
                <p style="margin:4px 0 0 0; font-size: 12px; color: #EF4444;">Needs Early Intervention</p>
            </div>
        """, unsafe_allow_html=True)

    with m4:
        top_name = stats['top_students'][0]['name'] if stats['top_students'] else "N/A"
        top_score = stats['top_students'][0]['score'] if stats['top_students'] else 0.0
        st.markdown(f"""
            <div style="background: white; border: 1px solid #E2E8F0; padding: 18px; border-radius: 10px; border-left: 5px solid #F59E0B;">
                <p style="margin:0; font-size: 13px; color: #64748B; font-weight: 600; text-transform: uppercase;">Top Performer</p>
                <h2 style="margin: 6px 0 0 0; font-size: 20px; font-weight: 700; color: #1E293B;">{top_name}</h2>
                <p style="margin:4px 0 0 0; font-size: 12px; color: #F59E0B; font-weight:700;">{top_score:.1f}% Avg</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Charts Section (Learning Level Distribution & Class Score Breakdown)
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("🍰 Learning-Level Distribution (Random Forest Predictions)")
        level_dist = stats['level_distribution']
        fig_pie = px.pie(
            values=list(level_dist.values()),
            names=list(level_dist.keys()),
            color=list(level_dist.keys()),
            color_discrete_map={'Beginner': '#F59E0B', 'Intermediate': '#3B82F6', 'Advanced': '#10B981'},
            hole=0.4,
            title="Class Proficiency Tiering"
        )
        fig_pie.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_pie, width="stretch")

    with col_chart2:
        st.subheader("📊 Individual Student Score Comparison")
        students_perf_df = query_to_dataframe("""
            SELECT s.name, AVG(q.score) as avg_score
            FROM students s
            LEFT JOIN quiz_results q ON s.id = q.student_id
            GROUP BY s.id
            ORDER BY avg_score DESC
        """)
        if not students_perf_df.empty:
            fig_bar = px.bar(
                students_perf_df,
                x='name',
                y='avg_score',
                labels={'name': 'Student', 'avg_score': 'Average Score (%)'},
                title="Student Performance Ranking",
                color='avg_score',
                color_continuous_scale='RdYlGn'
            )
            fig_bar.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_bar, width="stretch")

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. At-Risk Struggling Students Detection Section
    st.subheader("⚠️ Early Identification: Struggling Students (Needs Improvement)")
    st.caption("AI-identified students experiencing low quiz performance, high incorrect attempts, or low study time.")

    at_risk = stats['at_risk_students']
    if at_risk:
        for r in at_risk:
            st.markdown(f"""
                <div style="background: #FEF2F2; border: 1px solid #FCA5A5; border-left: 5px solid #EF4444; border-radius: 8px; padding: 16px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0; color: #991B1B; font-size: 18px;">👤 {r['name']}</h4>
                        <span style="background: #EF4444; color: white; padding: 4px 10px; border-radius: 12px; font-weight: 700; font-size: 12px;">{r['status']}</span>
                    </div>
                    <div style="margin-top: 8px; font-size: 14px; color: #7F1D1D;">
                        <strong>Average Score:</strong> {r['avg_score']}% &nbsp;|&nbsp; 
                        <strong>Weak Subject:</strong> {r['weak_subject']} &nbsp;|&nbsp; 
                        <strong>Study Time:</strong> {r['study_time']} hrs &nbsp;|&nbsp; 
                        <strong>Incorrect Attempts:</strong> {r['incorrect_attempts']}
                    </div>
                    <p style="margin: 8px 0 0 0; font-size: 13px; color: #991B1B; background: #FFE4E6; padding: 8px 12px; border-radius: 6px;">
                        💡 <strong>Diagnosis & Reason:</strong> {r['reason']}
                    </p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.success("🎉 All students are currently maintaining healthy academic progress!")

    st.markdown("<br>", unsafe_allow_html=True)

    # 4. Difficult Topics Analysis & Teaching Recommendations
    st.subheader("📌 Difficult Topics Analysis & Teaching Recommendations")
    difficult_topics = stats['difficult_topics']

    if difficult_topics:
        for dt in difficult_topics:
            st.markdown(f"""
                <div style="background: #FFFBEB; border: 1px solid #FDE68A; border-left: 5px solid #F59E0B; border-radius: 8px; padding: 16px; margin-bottom: 12px;">
                    <h4 style="margin: 0; color: #92400E; font-size: 17px;">Subject: {dt['subject']} — Topic: {dt['topic']}</h4>
                    <p style="margin: 6px 0; font-size: 14px; color: #78350F;">
                        <strong>Struggling Rate:</strong> <span style="color:#D97706; font-weight:700;">{dt['struggle_pct']}% of students struggling</span> (Topic Average: {dt['avg_score']}%)
                    </p>
                    <p style="margin: 4px 0 0 0; font-size: 13px; color: #92400E; background: #FEF3C7; padding: 8px 12px; border-radius: 6px;">
                        💡 <strong>AI Teacher Recommendation:</strong> {dt['recommendation']}
                    </p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No single topic currently exceeds difficulty thresholds across the class.")
