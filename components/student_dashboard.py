"""
Student Dashboard UI Component.
Displays overview metrics, Machine Learning classification badge, Plotly progress trends, and quick actions.
"""

import re

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.helpers import get_student_dashboard_data, identify_weak_subjects
from utils.gamification import get_gamification_summary
from components.ui import render_page_header

def render_student_dashboard(student_id):
    """Render Student Dashboard with metrics and performance breakdown."""
    dash_data = get_student_dashboard_data(student_id)
    if not dash_data:
        st.error("Failed to load student dashboard data.")
        return

    student_name = dash_data["name"]

    render_page_header(
        "STUDENT OVERVIEW",
        f"Welcome back, {student_name}",
        "Your learning snapshot, tailored recommendations, and progress in one place.",
        "👋",
    )

    gamification = get_gamification_summary(student_id)
    g1, g2, g3 = st.columns(3)
    g1.metric("Learning streak", f"🔥 {gamification['current_streak']} days")
    g2.metric("Learning XP", f"{gamification['total_points']} XP", f"Level {gamification['level']}")
    g3.metric("Achievements", f"{gamification['unlocked_badges']}/{gamification['total_badges']} unlocked")
    st.progress(gamification["points_in_level"] / 100)
    st.caption(f"{gamification['points_to_next_level']} XP to the next learning level · Complete quizzes, labs, and resources to earn XP.")

    # 1. Metric Cards Row
    m1, m2, m3, m4 = st.columns(4)

    level_color_map = {
        "Beginner": "🟡",
        "Intermediate": "🔵",
        "Advanced": "🟢"
    }
    icon = level_color_map.get(dash_data['learning_level'], "⭐")

    with m1:
        st.metric("AI Learning Level", f"{icon} {dash_data['learning_level']}", f"{dash_data['confidence']}% AI Confidence")

    with m2:
        st.metric("Quiz Average", f"{dash_data['avg_quiz_score']}%")

    with m3:
        st.metric("Assignment Average", f"{dash_data['avg_assign_score']}%")

    with m4:
        st.metric("Total Study Time", f"{dash_data['study_time']} hrs")

    st.markdown("---")

    # 2. Performance Breakdown & Plotly Chart
    col_chart1, col_chart2 = st.columns([3, 2])

    with col_chart1:
        st.subheader("🧩 Exam Performance by Subject & Level")
        quiz_history = dash_data.get("quiz_history", pd.DataFrame())
        needed_columns = {"subject", "topic", "score"}

        if not quiz_history.empty and needed_columns.issubset(quiz_history.columns):
            exam_scores = quiz_history.copy()
            exam_scores["difficulty"] = exam_scores["topic"].astype(str).str.extract(
                r"\b(Beginner|Intermediate|Advanced)\b", flags=re.IGNORECASE
            )[0].str.title()
            exam_scores["score"] = pd.to_numeric(exam_scores["score"], errors="coerce")
            exam_scores = exam_scores.dropna(subset=["subject", "difficulty", "score"])

            if not exam_scores.empty:
                level_order = ["Beginner", "Intermediate", "Advanced"]
                summary = (
                    exam_scores.groupby(["subject", "difficulty"], as_index=False)
                    .agg(average_score=("score", "mean"), exams=("score", "count"))
                )
                score_grid = summary.pivot(
                    index="subject", columns="difficulty", values="average_score"
                ).reindex(columns=level_order).sort_index()
                exam_grid = summary.pivot(
                    index="subject", columns="difficulty", values="exams"
                ).reindex(index=score_grid.index, columns=level_order)

                fig = go.Figure(
                    go.Heatmap(
                        z=score_grid.values,
                        x=level_order,
                        y=score_grid.index.tolist(),
                        customdata=exam_grid.values,
                        colorscale="Viridis",
                        zmin=0,
                        zmax=100,
                        colorbar={"title": "Score (%)"},
                        hovertemplate=(
                            "Subject: %{y}<br>Level: %{x}<br>"
                            "Average score: %{z:.1f}%<br>"
                            "Exams: %{customdata}<extra></extra>"
                        ),
                    )
                )
                fig.update_layout(
                    title="Average exam score by subject and difficulty",
                    xaxis_title="Exam level",
                    yaxis_title="Subject",
                    margin=dict(l=20, r=20, t=55, b=20),
                )
                fig.update_xaxes(side="top")
                fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig, width="stretch")
                st.caption(
                    "Each cell shows the average score for exams taken at that level. "
                    "Hover over a cell to see how many exams are included. "
                    "Older quiz results without a difficulty label are not included."
                )
            else:
                st.info(
                    "No level-tagged exam results yet. Take a Beginner, Intermediate, "
                    "or Advanced exam to see your subject-by-level performance here."
                )
        else:
            st.info("No level-tagged exam results yet. Complete a Beginner, Intermediate, or Advanced exam to populate this chart.")

    with col_chart2:
        st.subheader("🎯 Focus & Weak Subject Alerts")
        weak_list = identify_weak_subjects(student_id)

        if weak_list:
            st.warning("Subjects needing extra focus (< 50% score):")
            for w in weak_list:
                st.error(f"⚠️ **{w}** — Targeted practice quiz & video module available.")
        else:
            st.success("🎉 Outstanding work! All subjects are currently above 50%. Keep maintaining high scores!")

        st.markdown("---")
        st.subheader("🚀 Quick Actions")
        action_quiz, action_achievements = st.columns(2)
        with action_quiz:
            if st.button("Take Practice Quiz 📝", key="dash_btn_quiz", width="stretch"):
                st.session_state['pending_nav'] = "📝 Practice Quiz (Course-Wise)"
                st.rerun()
        with action_achievements:
            if st.button("View Goals & Achievements 🏆", key="dash_btn_achievements", width="stretch"):
                st.session_state['pending_nav'] = "🏆 Goals & Achievements"
                st.rerun()
