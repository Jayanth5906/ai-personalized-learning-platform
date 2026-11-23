"""
Database Schema Definitions for AI-Powered Personalized Learning Platform.
"""

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('student', 'teacher')),
    name TEXT NOT NULL
);
"""

CREATE_STUDENTS_TABLE = """
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    name TEXT NOT NULL,
    learning_level TEXT DEFAULT 'Intermediate',
    study_time REAL DEFAULT 0.0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

CREATE_SUBJECTS_TABLE = """
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_name TEXT UNIQUE NOT NULL
);
"""

CREATE_QUIZ_RESULTS_TABLE = """
CREATE TABLE IF NOT EXISTS quiz_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject TEXT NOT NULL,
    topic TEXT NOT NULL,
    score REAL NOT NULL,
    total_questions INTEGER NOT NULL,
    correct_answers INTEGER NOT NULL,
    incorrect_answers INTEGER NOT NULL,
    attempts INTEGER DEFAULT 1,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);
"""

CREATE_ASSIGNMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject TEXT NOT NULL,
    score REAL NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);
"""

CREATE_LEARNING_RESOURCES_TABLE = """
CREATE TABLE IF NOT EXISTS learning_resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    subject TEXT NOT NULL,
    topic TEXT NOT NULL,
    difficulty TEXT NOT NULL CHECK(difficulty IN ('Beginner', 'Intermediate', 'Advanced')),
    resource_type TEXT NOT NULL CHECK(resource_type IN ('Video', 'Notes', 'Quiz', 'Practice Questions', 'Previous Exam Questions')),
    description TEXT NOT NULL,
    url TEXT DEFAULT '#'
);
"""

CREATE_PROGRESS_TABLE = """
CREATE TABLE IF NOT EXISTS progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    resource_id INTEGER NOT NULL,
    completed INTEGER DEFAULT 0,
    completion_date TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (resource_id) REFERENCES learning_resources(id) ON DELETE CASCADE,
    UNIQUE(student_id, resource_id)
);
"""

CREATE_LEARNING_ACTIVITIES_TABLE = """
CREATE TABLE IF NOT EXISTS learning_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    activity_type TEXT NOT NULL CHECK(activity_type IN ('quiz', 'resource', 'assignment', 'lab', 'study_session')),
    source_id TEXT NOT NULL,
    title TEXT NOT NULL,
    points INTEGER NOT NULL DEFAULT 0,
    score REAL,
    activity_date TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE(student_id, activity_type, source_id)
);
"""

ALL_SCHEMA_QUERIES = [
    CREATE_USERS_TABLE,
    CREATE_STUDENTS_TABLE,
    CREATE_SUBJECTS_TABLE,
    CREATE_QUIZ_RESULTS_TABLE,
    CREATE_ASSIGNMENTS_TABLE,
    CREATE_LEARNING_RESOURCES_TABLE,
    CREATE_PROGRESS_TABLE,
    CREATE_LEARNING_ACTIVITIES_TABLE
]
