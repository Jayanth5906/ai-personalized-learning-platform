"""Student learning goals, activity streaks, XP, and achievement badges."""

from datetime import date, timedelta

import streamlit as st

from database.database import log_daily_study_session
from utils.gamification import get_gamification_summary
from components.ui import render_page_header


def render_achievements_page(student_id):
    """Render a student's personal learning streak and badge milestones."""
    summary = get_gamification_summary(student_id)

    render_page_header(
        "STUDENT WORKSPACE",
        "Learning goals & achievements",
        "Build a steady study habit, earn XP from learning activities, and unlock milestones as you progress.",
        "🏆",
    )

    if summary["today_active"]:
        st.info("Your learning activity for today is recorded and counts toward your streak.")

    if summary["today_study_checkin"]:
        st.success("Today's study session is logged. Come back tomorrow to keep your streak going!")
    elif st.button("✅ Log today's study session · +10 XP", type="primary", key="log_daily_study_session"):
        if log_daily_study_session(student_id):
            st.success("Study session logged. Your streak and XP have been updated.")
            st.rerun()
        else:
            st.info("Today's session has already been logged.")
            st.rerun()
    st.caption("Daily check-ins are self-reported and limited to one per day. Quizzes, labs, and completed resources also count toward your streak.")
    st.caption("XP rewards: quizzes 10–30 · assignments and resources 15 · practical labs 30 · daily check-in 10.")

    st.markdown("### Your learning progress")
    col_streak, col_longest, col_xp, col_badges = st.columns(4)
    col_streak.metric("Current streak", f"🔥 {summary['current_streak']} days")
    col_longest.metric("Longest streak", f"{summary['longest_streak']} days")
    col_xp.metric("Learning XP", f"{summary['total_points']} XP", f"Level {summary['level']}")
    col_badges.metric("Badges unlocked", f"{summary['unlocked_badges']}/{summary['total_badges']}")

    st.progress(summary["points_in_level"] / 100)
    st.caption(f"{summary['points_in_level']} / 100 XP toward Level {summary['level'] + 1} · {summary['points_to_next_level']} XP to go")

    st.markdown("### Your learning activity · last 14 days")
    today = date.today()
    for row_start in range(0, 14, 7):
        columns = st.columns(7)
        for offset, column in enumerate(columns):
            day = today - timedelta(days=13 - row_start - offset)
            if day in summary["active_days"]:
                column.markdown("🟩")
            else:
                column.markdown("⬜")
            column.caption(day.strftime("%a %d"))

    st.markdown("### Badge collection")
    badge_columns = st.columns(3)
    for index, badge in enumerate(summary["badges"]):
        with badge_columns[index % len(badge_columns)]:
            status = "✅" if badge["unlocked"] else "🔒"
            st.markdown(f"**{status} {badge['icon']} {badge['name']}**")
            st.caption(badge["description"])
            st.progress(badge["progress"])
            st.caption("Unlocked" if badge["unlocked"] else f"Progress: {badge['progress_text']}")

    st.markdown("### Recent activity")
    recent = summary["recent_activities"]
    if recent.empty:
        st.info("No learning activity yet. Complete a quiz, finish a resource, submit a lab, or log today's session to get started.")
    else:
        display = recent[["activity_date", "title", "activity_type", "points"]].rename(columns={
            "activity_date": "Date",
            "title": "Activity",
            "activity_type": "Type",
            "points": "XP",
        })
        st.dataframe(display, hide_index=True, width="stretch")

    st.markdown("### Keep learning")
    action_quiz, action_resources, action_labs = st.columns(3)
    with action_quiz:
        if st.button("Take a practice quiz 📝", key="achievements_go_quiz", width="stretch"):
            st.session_state["pending_nav"] = "📝 Practice Quiz (Course-Wise)"
            st.rerun()
    with action_resources:
        if st.button("Browse learning resources 📚", key="achievements_go_resources", width="stretch"):
            st.session_state["pending_nav"] = "📚 Learning Resources & Catalogue"
            st.rerun()
    with action_labs:
        if st.button("Try a practical lab 🧪", key="achievements_go_labs", width="stretch"):
            st.session_state["pending_nav"] = "🧪 Practical DE & AI Coding Labs"
            st.rerun()
