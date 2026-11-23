"""
Authentication and Session Management Module.
"""

import streamlit as st
from database.database import execute_single_query, get_connection

def authenticate_user(username, password):
    """
    Authenticate user credentials against SQLite users table.
    Returns user record dict if valid, else None.
    """
    query = "SELECT id, username, role, name FROM users WHERE username = ? AND password = ?"
    user = execute_single_query(query, (username.strip(), password.strip()))
    if user:
        return dict(user)
    return None

def get_student_by_user_id(user_id):
    """Fetch student record associated with a specific user_id."""
    query = "SELECT id, user_id, name, learning_level, study_time FROM students WHERE user_id = ?"
    stu = execute_single_query(query, (user_id,))
    if stu:
        return dict(stu)
    return None

def register_user(name, username, password, role):
    """
    Register a new user account in SQLite database.
    If role is 'student', creates a corresponding record in students table.
    """
    name = name.strip()
    username = username.strip()
    password = password.strip()
    role = role.strip().lower()

    if not name or not username or not password:
        return False, "All fields (Full Name, Username, Password) are required."

    if len(password) < 4:
        return False, "Password must be at least 4 characters long."

    if role not in ['student', 'teacher']:
        return False, "Invalid role specified."

    # Check if username already exists
    existing = execute_single_query("SELECT id FROM users WHERE username = ?", (username,))
    if existing:
        return False, f"Username '{username}' is already taken. Please choose another username."

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, password, role, name) VALUES (?, ?, ?, ?)",
            (username, password, role, name)
        )
        user_id = cursor.lastrowid

        if role == 'student':
            cursor.execute(
                "INSERT INTO students (user_id, name, learning_level, study_time) VALUES (?, ?, ?, ?)",
                (user_id, name, 'Beginner', 0.0)
            )

        conn.commit()
        conn.close()
        return True, f"Account for '{name}' ({role.title()}) created successfully! You can now sign in."
    except Exception as e:
        conn.close()
        return False, f"Failed to create account: {str(e)}"

def login_user(username, password):
    """Authenticate and store user details in Streamlit session state."""
    user_dict = authenticate_user(username, password)
    if user_dict:
        st.session_state['authenticated'] = True
        st.session_state['user'] = user_dict
        
        if user_dict['role'].lower() == 'student':
            stu = get_student_by_user_id(user_dict['id'])
            if stu:
                st.session_state['student_id'] = stu['id']
                st.session_state['student_name'] = stu['name']
                user_dict['student_id'] = stu['id']
        return user_dict
    return None

def get_current_user():
    """Retrieve currently authenticated user dict from session state."""
    return st.session_state.get('user')

def logout_user():
    """Clear Streamlit session state on logout."""
    st.session_state['authenticated'] = False
    st.session_state['user'] = None
    st.session_state['student_id'] = None
    st.session_state['student_name'] = None

def is_logged_in():
    """Check if user is currently authenticated in session state."""
    return st.session_state.get('authenticated', False) and st.session_state.get('user') is not None
