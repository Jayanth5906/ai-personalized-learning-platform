"""Learning activity summaries, XP, streaks, and badge milestones."""

from datetime import date, datetime, timedelta

from database.database import query_to_dataframe


BADGE_DEFINITIONS = [
    {"name": "First Steps", "icon": "🌱", "metric": "quizzes", "target": 1, "description": "Complete your first quiz."},
    {"name": "Quiz Explorer", "icon": "🧭", "metric": "quizzes", "target": 5, "description": "Complete 5 quizzes."},
    {"name": "Quiz Champion", "icon": "🏆", "metric": "quizzes", "target": 10, "description": "Complete 10 quizzes."},
    {"name": "Resource Collector", "icon": "📚", "metric": "resources", "target": 3, "description": "Complete 3 learning resources."},
    {"name": "Hands-on Learner", "icon": "🧪", "metric": "labs", "target": 2, "description": "Submit 2 practical labs."},
    {"name": "On a Roll", "icon": "🔥", "metric": "longest_streak", "target": 3, "description": "Learn on 3 consecutive days."},
    {"name": "Week of Learning", "icon": "🗓️", "metric": "longest_streak", "target": 7, "description": "Learn on 7 consecutive days."},
    {"name": "Perfect Score", "icon": "💯", "metric": "perfect_quizzes", "target": 1, "description": "Earn 100% on a quiz."},
]


def get_gamification_summary(student_id):
    """Return the student's activity totals, streaks, level, and badge progress."""
    activities = query_to_dataframe(
        """SELECT activity_type, title, points, score, activity_date
           FROM learning_activities WHERE student_id = ? ORDER BY activity_date DESC, id DESC""",
        (student_id,),
    )

    if activities.empty:
        activity_days = set()
        counts = {"quiz": 0, "resource": 0, "assignment": 0, "lab": 0}
        total_points = 0
        perfect_quizzes = 0
    else:
        parsed_days = set()
        for value in activities["activity_date"].dropna():
            try:
                parsed_days.add(datetime.strptime(str(value)[:10], "%Y-%m-%d").date())
            except ValueError:
                continue
        today = date.today()
        activity_days = {day for day in parsed_days if day <= today}
        counts = activities["activity_type"].value_counts().to_dict()
        counts = {name: int(counts.get(name, 0)) for name in ("quiz", "resource", "assignment", "lab")}
        total_points = int(activities["points"].fillna(0).sum())
        quiz_scores = activities.loc[activities["activity_type"] == "quiz", "score"].dropna()
        perfect_quizzes = int((quiz_scores >= 100).sum())

    today = date.today()
    longest_streak = 0
    running_streak = 0
    previous_day = None
    for active_day in sorted(activity_days):
        if previous_day is not None and active_day == previous_day + timedelta(days=1):
            running_streak += 1
        else:
            running_streak = 1
        longest_streak = max(longest_streak, running_streak)
        previous_day = active_day

    # A streak remains active until the end of the day after the last check-in.
    anchor = today if today in activity_days else today - timedelta(days=1)
    current_streak = 0
    while anchor in activity_days:
        current_streak += 1
        anchor -= timedelta(days=1)

    metric_values = {
        "quizzes": counts["quiz"],
        "resources": counts["resource"],
        "labs": counts["lab"],
        "longest_streak": longest_streak,
        "perfect_quizzes": perfect_quizzes,
    }
    badges = []
    for definition in BADGE_DEFINITIONS:
        progress = metric_values[definition["metric"]]
        target = definition["target"]
        badges.append({
            **definition,
            "progress": min(progress / target, 1.0),
            "progress_text": f"{min(progress, target)}/{target}",
            "unlocked": progress >= target,
        })

    level = (total_points // 100) + 1
    points_in_level = total_points % 100
    today_active = today in activity_days
    today_study_checkin = False
    if not activities.empty:
        today_study_checkin = bool(
            ((activities["activity_type"] == "study_session") &
             (activities["activity_date"].astype(str).str[:10] == today.isoformat())).any()
        )
    recent = activities.head(10).copy() if not activities.empty else activities

    return {
        "total_points": total_points,
        "level": level,
        "points_in_level": points_in_level,
        "points_to_next_level": 100 - points_in_level,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "today_active": today_active,
        "today_study_checkin": today_study_checkin,
        "active_days": activity_days,
        "badges": badges,
        "unlocked_badges": sum(badge["unlocked"] for badge in badges),
        "total_badges": len(badges),
        "recent_activities": recent,
    }
