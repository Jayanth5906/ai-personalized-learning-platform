"""
My Performance Monitoring UI Component — Data Engineering & AI Specialization.
Provides student performance analytics, historical progress trends, skill radar, and career readiness metrics.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.helpers import get_student_dashboard_data, identify_weak_subjects, identify_strong_subjects
from components.ui import render_page_header

def render_my_performance(student_id):
    """Render professional Data Engineering & AI student performance analytics dashboard."""
    data = get_student_dashboard_data(student_id)
    if not data:
        st.error("Student record not found.")
        return

    # Custom CSS for Professional Data Engineering & AI Aesthetic
    st.markdown("""
        <style>
            .de-badge {
                display: inline-block;
                background: linear-gradient(135deg, #4F46E5 0%, #06B6D4 100%);
                color: white;
                font-weight: 700;
                font-size: 12px;
                padding: 4px 12px;
                border-radius: 9999px;
                letter-spacing: 0.5px;
                text-transform: uppercase;
                margin-bottom: 8px;
            }
            .kpi-card {
                background: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
                padding: 18px 20px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }
            .kpi-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
            }
            .kpi-label {
                font-size: 13px;
                font-weight: 600;
                color: #64748B;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 6px;
            }
            .kpi-value {
                font-size: 28px;
                font-weight: 800;
                color: #0F172A;
                line-height: 1.2;
            }
            .kpi-sub {
                font-size: 12px;
                font-weight: 600;
                color: #10B981;
                margin-top: 6px;
            }
            .kpi-sub-neutral {
                font-size: 12px;
                font-weight: 500;
                color: #64748B;
                margin-top: 6px;
            }
            .tag-strong {
                background: #DCFCE7;
                color: #166534;
                border: 1px solid #86EFAC;
                padding: 4px 10px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 600;
                display: inline-block;
                margin-right: 6px;
                margin-bottom: 6px;
            }
            .tag-weak {
                background: #FEE2E2;
                color: #991B1B;
                border: 1px solid #FCA5A5;
                padding: 4px 10px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 600;
                display: inline-block;
                margin-right: 6px;
                margin-bottom: 6px;
            }
        </style>
    """, unsafe_allow_html=True)

    # 1. Performance overview
    render_page_header(
        "STUDENT INSIGHTS",
        "Performance & competencies",
        "Track your progress over time, understand your subject strengths, and choose your next learning focus.",
        "📈",
    )

    # 2. Executive KPI Cards
    c1, c2, c3, c4 = st.columns(4)

    overall_avg = data['overall_avg']
    grade_str = "Grade A+ (Top 5%)" if overall_avg >= 90 else ("Grade A (Top 15%)" if overall_avg >= 80 else ("Grade B" if overall_avg >= 70 else "Needs Focus"))

    with c1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Overall Mastery Index</div>
                <div class="kpi-value">{overall_avg}%</div>
                <div class="kpi-sub">🏆 {grade_str}</div>
            </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">AI Proficiency Tier</div>
                <div class="kpi-value">{data['learning_level']}</div>
                <div class="kpi-sub">🤖 {data['confidence']}% Model Confidence</div>
            </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">DE & AI Lab Hours</div>
                <div class="kpi-value">{data['study_time']} hrs</div>
                <div class="kpi-sub-neutral">⏱️ Practical Code Execution</div>
            </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Completed Modules</div>
                <div class="kpi-value">{data['completed_resources']}</div>
                <div class="kpi-sub">✅ Learning Tracks Completed</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # 3. Multi-Tab Analytics Dashboard
    tab_skills, tab_trend, tab_log, tab_career = st.tabs([
        "📊 Competency Radar & Skill Matrix",
        "📈 Learning Velocity & Progress",
        "📋 Assessment & Quiz Log",
        "🎯 AI & DE Career Readiness"
    ])

    # ----------------------------------------------------
    # TAB 1: COMPETENCY RADAR & DOMAIN SKILL MATRIX
    # ----------------------------------------------------
    with tab_skills:
        col_radar, col_skills = st.columns([1.2, 1])

        perf = data['subject_performance']
        
        # Map general subjects to Data Engineering & AI Domain Competencies
        de_ai_skill_mapping = {
            "Python": "Python & Data Pipelines",
            "Data Structures": "Algorithms & Optimization",
            "DBMS": "SQL & Data Warehousing",
            "Algorithms": "Distributed Systems & Logic",
            "Java": "Backend Data Processing",
            "Machine Learning": "AI Models & MLOps"
        }

        skill_scores = {}
        if perf:
            for sub, score in perf.items():
                mapped_name = de_ai_skill_mapping.get(sub, sub)
                skill_scores[mapped_name] = score
        else:
            skill_scores = {
                "Python & Data Pipelines": 85,
                "SQL & Data Warehousing": 78,
                "AI Models & MLOps": 82,
                "Algorithms & Optimization": 75,
                "Backend Data Processing": 70
            }

        with col_radar:
            st.subheader("🎯 Data Engineering & AI Skill Radar")
            categories = list(skill_scores.keys())
            values = list(skill_scores.values())

            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill='toself',
                name='Competency Score',
                fillcolor='rgba(79, 70, 229, 0.25)',
                line=dict(color='#4F46E5', width=3)
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        tickfont=dict(size=10, color="#64748B"),
                        gridcolor="#E2E8F0"
                    ),
                    angularaxis=dict(
                        tickfont=dict(size=11, color="#1E293B", weight="bold")
                    )
                ),
                showlegend=False,
                height=380,
                margin=dict(l=40, r=40, t=30, b=30)
            )
            st.plotly_chart(fig_radar, width="stretch")

        with col_skills:
            st.subheader("⚡ Core Domain Skill Breakdown")
            st.caption("Detailed proficiency scores across Data Engineering & AI sub-fields:")

            for name, score in skill_scores.items():
                status_icon = "🟢" if score >= 75 else ("🟡" if score >= 50 else "🔴")
                st.markdown(f"**{status_icon} {name}**: `{score}%`")
                st.progress(min(1.0, max(0.0, score / 100.0)))

            st.markdown("<br>", unsafe_allow_html=True)
            
            strong_subs = identify_strong_subjects(student_id)
            weak_subs = identify_weak_subjects(student_id)

            st.markdown("**Key Competency Status:**")
            if strong_subs:
                for s in strong_subs:
                    st.markdown(f'<span class="tag-strong">✓ Strong: {s}</span>', unsafe_allow_html=True)
            if weak_subs:
                for w in weak_subs:
                    st.markdown(f'<span class="tag-weak">⚠️ Focus: {w}</span>', unsafe_allow_html=True)
            if not strong_subs and not weak_subs:
                st.caption("Consistent average performance across all registered modules.")

    # ----------------------------------------------------
    # TAB 2: LEARNING VELOCITY & PROGRESS TRENDS
    # ----------------------------------------------------
    with tab_trend:
        st.subheader("📅 Weekly Assessment Score Improvement Trend")
        q_hist = data['quiz_history']

        if not q_hist.empty:
            fig_line = px.line(
                q_hist,
                x='date',
                y='score',
                color='subject',
                markers=True,
                title='Score Trajectory by Subject over Time',
                labels={'date': 'Date of Assessment', 'score': 'Score (%)', 'subject': 'Course Track'},
                color_discrete_sequence=['#4F46E5', '#06B6D4', '#10B981', '#F59E0B', '#EC4899']
            )
            fig_line.update_layout(
                yaxis_range=[0, 105],
                height=380,
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_line, width="stretch")
        else:
            st.info("No historical quiz data recorded yet.")

        st.markdown("<br>", unsafe_allow_html=True)

        # Theoretical Quizzes vs Practical Assignments
        col_comp1, col_comp2 = st.columns(2)
        with col_comp1:
            st.subheader("📝 Theoretical vs Practical Hands-on Performance")
            avg_q = data['avg_quiz_score']
            avg_a = data['avg_assign_score']

            fig_comp = px.bar(
                x=['Quiz Assessments', 'Practical Lab Assignments'],
                y=[avg_q, avg_a],
                labels={'x': 'Evaluation Metric', 'y': 'Average Score (%)'},
                color=['Quiz Assessments', 'Practical Lab Assignments'],
                color_discrete_sequence=['#4F46E5', '#06B6D4'],
                text=[f"{avg_q}%", f"{avg_a}%"]
            )
            fig_comp.update_traces(textposition='outside', textfont_size=13, textfont_weight='bold')
            fig_comp.update_layout(
                yaxis_range=[0, 115],
                showlegend=False,
                height=340,
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_comp, width="stretch")

        with col_comp2:
            st.subheader("💡 Learning Insights & Velocity Summary")
            st.markdown(f"""
                - **Quiz Mastery Rate:** Current average quiz accuracy is **{avg_q}%**.
                - **Lab Execution Score:** Practical assignment score averages **{avg_a}%**.
                - **Learning Velocity Status:** Student exhibits strong problem-solving capabilities with a predicted **{data['learning_level']}** learning level.
                - **Recommended Action:** Continue practicing 20-bit course tests to maintain top-tier performance index.
            """)

    # ----------------------------------------------------
    # TAB 3: PRACTICAL ASSESSMENT & QUIZ LOG
    # ----------------------------------------------------
    with tab_log:
        st.subheader("📋 Comprehensive Assessment History Log")
        if not q_hist.empty:
            # Display clean formatted table
            q_display = q_hist.copy()
            q_display.rename(columns={
                'date': 'Date',
                'subject': 'Subject Track',
                'topic': 'Topic',
                'score': 'Score (%)',
                'total_questions': 'Total Qs',
                'correct_answers': 'Correct',
                'incorrect_answers': 'Incorrect',
                'attempts': 'Attempt Count'
            }, inplace=True)
            
            st.dataframe(
                q_display[['Date', 'Subject Track', 'Topic', 'Score (%)', 'Total Qs', 'Correct', 'Incorrect', 'Attempt Count']],
                width="stretch"
            )

            # Summary Metrics below table
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Total Tests Taken", len(q_hist))
            with m2:
                avg_score_val = round(q_hist['score'].mean(), 1)
                st.metric("Average Quiz Score", f"{avg_score_val}%")
            with m3:
                total_correct = q_hist['correct_answers'].sum()
                total_qs = q_hist['total_questions'].sum()
                accuracy = round((total_correct / total_qs * 100), 1) if total_qs > 0 else 0
                st.metric("Overall Accuracy Rate", f"{accuracy}%")
        else:
            st.info("No quiz history logs available.")

    # ----------------------------------------------------
    # TAB 4: CAREER READINESS & AI RECOMMENDATIONS
    # ----------------------------------------------------
    with tab_career:
        st.subheader("🎯 Data Engineering & AI Career Readiness Index")
        
        # Calculate dynamic readiness index based on overall score and completed modules
        readiness_score = min(100, int(overall_avg * 0.7 + (data['completed_resources'] / 8.0) * 30))
        readiness_tier = "Senior Industry Ready" if readiness_score >= 85 else ("Junior / Associate Ready" if readiness_score >= 70 else "In Training")

        col_read1, col_read2 = st.columns([1, 1.2])

        with col_read1:
            st.markdown(f"""
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 24px; border-radius: 12px; text-align: center;">
                    <h4 style="color: #64748B; margin-bottom: 4px;">Role Readiness Index</h4>
                    <h1 style="color: #4F46E5; font-size: 48px; margin: 0; font-weight: 800;">{readiness_score}%</h1>
                    <div style="color: #10B981; font-weight: 700; font-size: 16px; margin-top: 8px;">🚀 Status: {readiness_tier}</div>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.progress(readiness_score / 100.0)

        with col_read2:
            st.markdown("### 🎓 Recommended Next Steps for Career Readiness")
            weak_subs = identify_weak_subjects(student_id)
            if weak_subs:
                st.warning(f"Focus on strengthening weak subjects to boost readiness: **{', '.join(weak_subs)}**.")
            else:
                st.success("🎉 Excellent! All domain scores meet or exceed baseline industry expectations.")

            st.markdown("""
                - **Data Pipeline Mastery:** Complete all PySpark & SQL optimization exercises in the catalogue.
                - **AI & MLOps Integration:** Build end-to-end model inference pipelines using Python.
                - **Continuous Testing:** Complete 20-bit quizzes weekly to reinforce memory retention.
            """)
