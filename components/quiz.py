"""
Timed course exam UI with browser fullscreen and a two-switch allowance.
"""

from math import ceil
from pathlib import Path
from time import time
from uuid import uuid4

import streamlit as st
import streamlit.components.v1 as components

from components.quiz_bank import QUIZ_BANK
from components.ui import render_page_header
from database.database import save_quiz_result
from ml.predictor import predict_learning_level

EXAM_DURATION_SECONDS = 30 * 60
ALLOWED_FOCUS_STRIKES = 2
exam_controls = components.declare_component(
    "learnwise_exam_controls",
    path=str(Path(__file__).with_name("exam_controls")),
)


def _answer_key(run_id, question_index):
    return f"exam_answer_{run_id}_{question_index}"


def _initialize_exam_state():
    defaults = {
        "quiz_active": False,
        "quiz_deadline": None,
        "quiz_course": list(QUIZ_BANK.keys())[0],
        "quiz_difficulty": "Beginner",
        "quiz_switch_count": 0,
        "quiz_run_id": None,
        "quiz_result": None,
        "quiz_control_event_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _complete_exam(student_id, reason):
    """Grade and persist the current attempt once, using answers saved on each selection."""
    if not st.session_state.get("quiz_active"):
        return

    course = st.session_state.quiz_course
    difficulty = st.session_state.quiz_difficulty
    run_id = st.session_state.quiz_run_id
    questions = QUIZ_BANK[course][difficulty]
    answers = {
        index: st.session_state.get(_answer_key(run_id, index))
        for index in range(1, len(questions) + 1)
    }
    correct_count = sum(
        answers[index] == question["answer"]
        for index, question in enumerate(questions, 1)
    )
    total_questions = len(questions)
    incorrect_count = total_questions - correct_count
    score = round((correct_count / max(total_questions, 1)) * 100, 1)

    result = {
        "course": course,
        "difficulty": difficulty,
        "run_id": run_id,
        "answers": answers,
        "correct": correct_count,
        "incorrect": incorrect_count,
        "total": total_questions,
        "score": score,
        "reason": reason,
        "switch_count": st.session_state.quiz_switch_count,
        "prediction": None,
        "save_error": None,
    }

    # Mark the attempt complete before calls that could fail, so it cannot save twice.
    st.session_state.quiz_active = False
    st.session_state.quiz_deadline = None
    st.session_state.quiz_result = result

    try:
        save_quiz_result(
            student_id=student_id,
            subject=course,
            topic=f"{difficulty} Timed Exam",
            score=score,
            total_questions=total_questions,
            correct_answers=correct_count,
            incorrect_answers=incorrect_count,
            attempts=1,
        )
    except Exception as exc:
        result["save_error"] = str(exc)

    try:
        result["prediction"] = predict_learning_level(student_id=student_id)
    except Exception:
        result["prediction"] = None


def _handle_control_event(event, student_id, course, difficulty):
    """Apply a new event from the browser component to the Streamlit exam session."""
    if not isinstance(event, dict):
        return None

    event_id = event.get("event_id")
    if not event_id or event_id == st.session_state.quiz_control_event_id:
        return None
    st.session_state.quiz_control_event_id = event_id

    event_type = event.get("type")
    if event_type == "start" and not st.session_state.quiz_active:
        st.session_state.quiz_course = course
        st.session_state.quiz_difficulty = difficulty
        st.session_state.quiz_run_id = uuid4().hex
        st.session_state.quiz_deadline = time() + EXAM_DURATION_SECONDS
        st.session_state.quiz_switch_count = 0
        st.session_state.quiz_result = None
        st.session_state.quiz_active = True
        return "started"

    if not st.session_state.quiz_active:
        return None

    if event_type == "strike":
        st.session_state.quiz_switch_count += 1
        if st.session_state.quiz_switch_count > ALLOWED_FOCUS_STRIKES:
            _complete_exam(student_id, "switch_limit")
            return "completed"
        return "strike"

    if event_type == "time_expired":
        _complete_exam(student_id, "time_limit")
        return "completed"

    return None


def _render_exam_result(student_id):
    result = st.session_state.quiz_result
    if not result:
        return

    reason_copy = {
        "submitted": "You submitted the exam.",
        "time_limit": "The 30-minute timer reached zero. Your saved answers were submitted.",
        "switch_limit": "The two-warning limit was exceeded. Your saved answers were submitted.",
    }
    render_page_header(
        "EXAM COMPLETE",
        "Your results",
        reason_copy.get(result["reason"], "Your exam attempt is complete."),
        "✅",
    )

    summary_cols = st.columns(3)
    summary_cols[0].metric("Final score", f'{result["score"]}%')
    summary_cols[1].metric("Correct answers", f'{result["correct"]}/{result["total"]}')
    summary_cols[2].metric("Focus/fullscreen warnings", f'{result["switch_count"]}/{ALLOWED_FOCUS_STRIKES + 1}')

    st.caption(f'{result["course"]} · {result["difficulty"]} · {result["total"]} questions')
    if result["save_error"]:
        st.error("The attempt was graded, but the result could not be saved to the learning record.")
    else:
        st.success("Your exam result has been saved.")

    prediction = result.get("prediction")
    if prediction:
        st.info(
            f'Updated learning level: {prediction.get("learning_level", "Unavailable")} '
            f'({prediction.get("confidence", "—")}% confidence)'
        )

    with st.expander("Review answers", expanded=True):
        questions = QUIZ_BANK[result["course"]][result["difficulty"]]
        for index, question in enumerate(questions, 1):
            selected = result["answers"].get(index)
            if selected == question["answer"]:
                st.success(f'Question {index}: Correct — {selected}')
            elif selected is None:
                st.warning(f'Question {index}: Not answered. Correct answer: {question["answer"]}')
            else:
                st.error(f'Question {index}: Your answer: {selected} · Correct answer: {question["answer"]}')
            st.markdown(question["explanation"])
            if index < len(questions):
                st.divider()

    if st.button("Start another exam", type="primary", width="stretch", key="start_another_exam"):
        st.session_state.quiz_result = None
        st.session_state.quiz_run_id = None
        st.session_state.quiz_switch_count = 0
        st.rerun()


def render_practice_quiz(student_id):
    """Render a 30-minute exam with a live browser timer and basic focus safeguards."""
    _initialize_exam_state()
    render_page_header(
        "PRACTICE & ASSESSMENT",
        "Course exams",
        "Choose a course and difficulty, then take a timed, fullscreen exam.",
        "📝",
    )

    if st.session_state.quiz_result and not st.session_state.quiz_active:
        _render_exam_result(student_id)
        return

    if st.session_state.quiz_active:
        deadline = st.session_state.quiz_deadline or time()
        if time() >= deadline:
            _complete_exam(student_id, "time_limit")
            _render_exam_result(student_id)
            return

        course = st.session_state.quiz_course
        difficulty = st.session_state.quiz_difficulty
        questions = QUIZ_BANK[course][difficulty]

        event_result = exam_controls(
            active=True,
            deadline_ms=int(deadline * 1000),
            server_now_ms=int(time() * 1000),
            switch_count=st.session_state.quiz_switch_count,
            allowed_switches=ALLOWED_FOCUS_STRIKES,
            key="learnwise_exam_controls",
            default=None,
        )
        event_status = _handle_control_event(event_result, student_id, course, difficulty)
        if event_status == "completed" or not st.session_state.quiz_active:
            _render_exam_result(student_id)
            return

        header_col, cancel_col = st.columns([5, 1])
        with header_col:
            st.subheader(f'{course} · {difficulty} exam')
            st.caption(
                f'{len(questions)} questions · 30 minutes · '
                f'{ALLOWED_FOCUS_STRIKES} warnings allowed; the next focus/fullscreen violation submits the exam.'
            )
        with cancel_col:
            if st.button("Cancel exam", key="cancel_exam"):
                st.session_state.quiz_active = False
                st.session_state.quiz_deadline = None
                st.session_state.quiz_result = None
                st.rerun()

        answered = sum(
            st.session_state.get(_answer_key(st.session_state.quiz_run_id, index)) is not None
            for index in range(1, len(questions) + 1)
        )
        st.progress(answered / max(len(questions), 1), text=f"{answered} of {len(questions)} answered")

        for index, question in enumerate(questions, 1):
            st.markdown(f"#### Question {index} of {len(questions)}")
            st.markdown(question["question"])
            st.radio(
                f"Answer for question {index}",
                question["options"],
                index=None,
                key=_answer_key(st.session_state.quiz_run_id, index),
                label_visibility="collapsed",
            )
            if index < len(questions):
                st.divider()

        if st.button("Submit exam", type="primary", width="stretch", key="submit_timed_exam"):
            _complete_exam(student_id, "submitted")
            st.rerun()
        return

    if st.session_state.quiz_result is None:
        setup_course, setup_difficulty = st.columns(2)
        with setup_course:
            course = st.selectbox("Course", list(QUIZ_BANK.keys()), key="exam_course_setup")
        with setup_difficulty:
            difficulty = st.selectbox(
                "Difficulty",
                ["Beginner", "Intermediate", "Advanced"],
                key="exam_difficulty_setup",
            )

        questions = QUIZ_BANK[course][difficulty]
        info_cols = st.columns(3)
        info_cols[0].metric("Questions", len(questions))
        info_cols[1].metric("Time limit", "30 min")
        info_cols[2].metric("Switch warnings", "2 allowed")

        st.info(
            "The exam uses browser fullscreen and counts tab switches or fullscreen exits. "
            "Two warnings are allowed; the next violation submits your saved answers. "
            "No camera, microphone, or screen recording is used."
        )

        start_event = exam_controls(
            active=False,
            deadline_ms=0,
            server_now_ms=int(time() * 1000),
            switch_count=0,
            allowed_switches=ALLOWED_FOCUS_STRIKES,
            key="learnwise_exam_controls",
            default=None,
        )
        event_status = _handle_control_event(start_event, student_id, course, difficulty)
        if event_status == "started":
            st.rerun()

