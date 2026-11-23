"""
Database Management Module for SQLite Operations and Sample Data Seeding.
"""

import sqlite3
import os
import pandas as pd
from database.schema import ALL_SCHEMA_QUERIES

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database.db")

def get_connection():
    """Establish and return a SQLite database connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables, migrate legacy URLs, and populate sample data if empty."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Execute all table creation statements
    for query in ALL_SCHEMA_QUERIES:
        cursor.execute(query)
        
    conn.commit()
    
    # Check if users exist; if not, seed sample data
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    if user_count == 0:
        seed_sample_data(conn)

    # Preserve achievements and activity streaks for students already in the database.
    backfill_learning_activities(conn)

    # Migrate any legacy example.com URLs to real YouTube embed links
    cursor.execute("UPDATE learning_resources SET url = 'https://www.youtube.com/embed/ngCos392W4w' WHERE url LIKE '%example.com%' AND (subject = 'Algorithms' OR subject = 'Data Structures')")
    cursor.execute("UPDATE learning_resources SET url = 'https://www.youtube.com/embed/eIrMbAQSU34' WHERE url LIKE '%example.com%' AND (subject = 'Java' OR subject = 'Machine Learning')")
    cursor.execute("UPDATE learning_resources SET url = 'https://www.youtube.com/embed/rfscVS0vtbw' WHERE url LIKE '%example.com%' AND subject = 'Python'")
    cursor.execute("UPDATE learning_resources SET url = 'https://www.youtube.com/embed/GFQaEYEc8_8' WHERE url LIKE '%example.com%' AND subject = 'DBMS'")
    conn.commit()
        
    conn.close()

def backfill_learning_activities(conn):
    """Create idempotent activity records for quiz, assignment, and resource history."""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO learning_activities
            (student_id, activity_type, source_id, title, points, score, activity_date, created_at)
        SELECT student_id, 'quiz', CAST(id AS TEXT), subject || ' quiz · ' || topic,
               10 + CAST(ROUND(MAX(0, MIN(20, score / 5.0))) AS INTEGER), score,
               substr(COALESCE(date, date('now', 'localtime')), 1, 10), COALESCE(date, CURRENT_TIMESTAMP)
        FROM quiz_results
    """)
    cursor.execute("""
        INSERT OR IGNORE INTO learning_activities
            (student_id, activity_type, source_id, title, points, score, activity_date, created_at)
        SELECT student_id, 'assignment', CAST(id AS TEXT), subject || ' assignment', 15, score,
               substr(COALESCE(date, date('now', 'localtime')), 1, 10), COALESCE(date, CURRENT_TIMESTAMP)
        FROM assignments
    """)
    cursor.execute("""
        INSERT OR IGNORE INTO learning_activities
            (student_id, activity_type, source_id, title, points, activity_date, created_at)
        SELECT p.student_id, 'resource', CAST(p.id AS TEXT), r.title || ' completed', 15,
               substr(COALESCE(p.completion_date, date('now', 'localtime')), 1, 10),
               COALESCE(p.completion_date, CURRENT_TIMESTAMP)
        FROM progress p
        JOIN learning_resources r ON r.id = p.resource_id
        WHERE p.completed = 1
    """)
    conn.commit()

def seed_sample_data(conn):
    """Seed sample realistic users, students, subjects, quizzes, assignments, and learning resources."""
    cursor = conn.cursor()
    
    # 1. Seed Subjects
    subjects = ["Java", "Python", "DBMS", "Data Structures", "Algorithms", "Machine Learning"]
    for sub in subjects:
        cursor.execute("INSERT OR IGNORE INTO subjects (subject_name) VALUES (?)", (sub,))
        
    # 2. Seed Users & Students
    # Teachers
    cursor.execute("INSERT INTO users (username, password, role, name) VALUES (?, ?, ?, ?)",
                   ('teacher1', 'teacher123', 'teacher', 'Dr. Rajesh Sharma'))
    cursor.execute("INSERT INTO users (username, password, role, name) VALUES (?, ?, ?, ?)",
                   ('teacher2', 'teacher123', 'teacher', 'Prof. Sunita Rao'))

    # 10 Students with varied characteristics
    students_data = [
        # (username, password, name, learning_level, study_time_hours)
        ('student1', 'student123', 'Aarav Patel', 'Advanced', 24.5),
        ('student2', 'student123', 'Ananya Gupta', 'Intermediate', 14.0),
        ('student3', 'student123', 'Rahul Sharma', 'Beginner', 4.5),      # Struggling
        ('student4', 'student123', 'Priya Verma', 'Intermediate', 16.5),
        ('student5', 'student123', 'Rohan Mehta', 'Beginner', 6.0),       # Struggling in Recursion
        ('student6', 'student123', 'Sneha Kapoor', 'Intermediate', 12.5),
        ('student7', 'student123', 'Vikram Singh', 'Beginner', 5.0),       # Struggling
        ('student8', 'student123', 'Kavya Joshi', 'Advanced', 28.0),
        ('student9', 'student123', 'Aditya Roy', 'Beginner', 7.2),         # Struggling in Recursion
        ('student10', 'student123', 'Neha Reddy', 'Intermediate', 15.0),
    ]

    student_id_map = {}
    for idx, (uname, pwd, sname, level, stime) in enumerate(students_data, 1):
        cursor.execute("INSERT INTO users (username, password, role, name) VALUES (?, ?, ?, ?)",
                       (uname, pwd, 'student', sname))
        user_id = cursor.lastrowid
        cursor.execute("INSERT INTO students (user_id, name, learning_level, study_time) VALUES (?, ?, ?, ?)",
                       (user_id, sname, level, stime))
        student_id = cursor.lastrowid
        student_id_map[uname] = student_id

    # 3. Seed Learning Resources
    resources_data = [
        # Java
        ("Java Fundamentals Video", "Java", "Basics", "Beginner", "Video", "Complete overview of Java syntax, variables, and data types.", "https://www.youtube.com/embed/eIrMbAQSU34"),
        ("Java OOP Concepts Guide", "Java", "OOP", "Intermediate", "Notes", "Detailed documentation on Abstraction, Encapsulation, Inheritance, and Polymorphism.", "https://www.youtube.com/embed/pTB0EiLXUC8"),
        ("Java Beginner Practice Questions", "Java", "Basics", "Beginner", "Practice Questions", "50 interactive beginner-friendly practice questions on Java loop and control flow.", "https://www.youtube.com/embed/eIrMbAQSU34"),
        ("Java Memory Management & Garbage Collection", "Java", "JVM", "Advanced", "Notes", "In-depth guide on JVM architecture, Heap vs Stack memory, and GC tuning.", "https://www.youtube.com/embed/pTB0EiLXUC8"),

        # Python
        ("Python Crash Course Video", "Python", "Basics", "Beginner", "Video", "Fast-paced video introduction to Python syntax, functions, and modules.", "https://www.youtube.com/embed/rfscVS0vtbw"),
        ("Python Data Structures & List Comprehensions", "Python", "Data Structures", "Intermediate", "Notes", "Master lists, dicts, tuples, sets, and functional constructs.", "https://www.youtube.com/embed/rfscVS0vtbw"),
        ("Python Decorators & Generators Masterclass", "Python", "Advanced Topics", "Advanced", "Notes", "Deep dive into python closure mechanics and custom generators.", "https://www.youtube.com/embed/rfscVS0vtbw"),

        # DBMS
        ("Database Fundamentals & ER Models", "DBMS", "Basics", "Beginner", "Notes", "Comprehensive introduction to relational databases and entity relationship diagrams.", "https://www.youtube.com/embed/GFQaEYEc8_8"),
        ("DBMS Normalization Videos", "DBMS", "Normalization", "Intermediate", "Video", "Step-by-step video breakdown of 1NF, 2NF, 3NF, and BCNF with examples.", "https://www.youtube.com/embed/GFQaEYEc8_8"),
        ("SQL Practice Quizzes & Queries", "DBMS", "SQL", "Intermediate", "Quiz", "Practice writing complex SQL JOINs, GROUP BY, and Subqueries.", "https://www.youtube.com/embed/GFQaEYEc8_8"),
        ("Previous Exam Questions on DBMS", "DBMS", "Transactions", "Advanced", "Previous Exam Questions", "Solved exam papers covering ACID properties, Indexing, and Concurrency Control.", "https://www.youtube.com/embed/GFQaEYEc8_8"),

        # Data Structures
        ("Arrays and Linked Lists Basics", "Data Structures", "Arrays", "Beginner", "Notes", "Linear data structures visual guide with array vs linked list comparison.", "https://www.youtube.com/embed/ngCos392W4w"),
        ("Recursion Fundamentals & Visualizer", "Data Structures", "Recursion", "Beginner", "Video", "Step-by-step video explaining call stacks, base cases, and recursive trees.", "https://www.youtube.com/embed/ngCos392W4w"),
        ("Binary Trees & BST Masterclass", "Data Structures", "Trees", "Intermediate", "Video", "Interactive video explaining binary tree traversals (Inorder, Preorder, Postorder) and BST ops.", "https://www.youtube.com/embed/fAAZixBzVSc"),
        ("Graph Algorithms & Shortest Path Notes", "Data Structures", "Graphs", "Advanced", "Notes", "In-depth analysis of BFS, DFS, Dijkstra's algorithm, and MST.", "https://www.youtube.com/embed/fAAZixBzVSc"),

        # Algorithms
        ("Sorting & Searching Algorithms Video", "Algorithms", "Sorting", "Beginner", "Video", "Visual animations of Bubble Sort, Merge Sort, and Binary Search.", "https://www.youtube.com/embed/ngCos392W4w"),
        ("Dynamic Programming for Beginners", "Algorithms", "DP", "Advanced", "Notes", "Overlapping subproblems, memoization vs tabulation with classic examples.", "https://www.youtube.com/embed/ngCos392W4w"),

        # Machine Learning
        ("Introduction to Machine Learning Concepts", "Machine Learning", "Intro", "Beginner", "Video", "Supervised vs Unsupervised learning overview for beginners.", "https://www.youtube.com/embed/eIrMbAQSU34"),
        ("Scikit-Learn Random Forest Tutorial", "Machine Learning", "Ensemble", "Intermediate", "Notes", "Building decision tree ensembles using Python Scikit-Learn.", "https://www.youtube.com/embed/eIrMbAQSU34")
    ]

    res_id_map = {}
    for title, subj, topic, diff, rtype, desc, url in resources_data:
        cursor.execute("""
            INSERT INTO learning_resources (title, subject, topic, difficulty, resource_type, description, url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (title, subj, topic, diff, rtype, desc, url))
        res_id_map[title] = cursor.lastrowid

    # 4. Seed Quiz Results & Assignments for Each Student
    # Standard date format
    dates = ["2026-08-01", "2026-08-03", "2026-08-05", "2026-08-08", "2026-08-10"]

    # Student Performance profiles
    # (uname, [quiz_records], [assignment_records])
    perf_profiles = [
        # Student 1: Aarav (High performer)
        ('student1', [
            ("Java", "OOP", 92, 10, 9, 1, 1, dates[0]),
            ("Python", "Basics", 95, 10, 10, 0, 1, dates[1]),
            ("DBMS", "SQL", 88, 10, 9, 1, 1, dates[2]),
            ("Data Structures", "Trees", 90, 10, 9, 1, 1, dates[3]),
            ("Algorithms", "Sorting", 94, 10, 9, 1, 1, dates[4])
        ], [
            ("Java", 90, dates[0]), ("Python", 96, dates[1]), ("DBMS", 85, dates[2]), ("Data Structures", 92, dates[3])
        ]),

        # Student 2: Ananya (Intermediate)
        ('student2', [
            ("Java", "OOP", 75, 10, 7, 3, 1, dates[0]),
            ("Python", "Basics", 82, 10, 8, 2, 1, dates[1]),
            ("DBMS", "SQL", 68, 10, 7, 3, 2, dates[2]),
            ("Data Structures", "Arrays", 72, 10, 7, 3, 1, dates[3]),
            ("Algorithms", "Sorting", 65, 10, 6, 4, 2, dates[4])
        ], [
            ("Java", 78, dates[0]), ("Python", 80, dates[1]), ("DBMS", 65, dates[2]), ("Data Structures", 70, dates[3])
        ]),

        # Student 3: Rahul (Struggling - Low score, high incorrect, high attempts)
        ('student3', [
            ("Java", "Basics", 42, 10, 4, 6, 4, dates[0]),
            ("DBMS", "Normalization", 38, 10, 3, 7, 5, dates[1]),
            ("Python", "Basics", 48, 10, 5, 5, 3, dates[2]),
            ("Data Structures", "Arrays", 40, 10, 4, 6, 4, dates[3]),
            ("DBMS", "SQL", 35, 10, 3, 7, 6, dates[4])
        ], [
            ("Java", 45, dates[0]), ("DBMS", 38, dates[1]), ("Python", 50, dates[2]), ("Data Structures", 42, dates[3])
        ]),

        # Student 4: Priya (High in Python, weak in DBMS)
        ('student4', [
            ("Python", "Basics", 88, 10, 9, 1, 1, dates[0]),
            ("Java", "OOP", 70, 10, 7, 3, 1, dates[1]),
            ("DBMS", "Normalization", 42, 10, 4, 6, 3, dates[2]),
            ("DBMS", "SQL", 45, 10, 4, 6, 4, dates[3]),
            ("Data Structures", "Arrays", 75, 10, 7, 3, 1, dates[4])
        ], [
            ("Python", 90, dates[0]), ("Java", 72, dates[1]), ("DBMS", 40, dates[2]), ("Data Structures", 78, dates[3])
        ]),

        # Student 5: Rohan (Struggling in Data Structures / Recursion)
        ('student5', [
            ("Python", "Basics", 65, 10, 6, 4, 2, dates[0]),
            ("Data Structures", "Recursion", 35, 10, 3, 7, 5, dates[1]),
            ("Data Structures", "Recursion", 40, 10, 4, 6, 4, dates[2]),
            ("Java", "Basics", 58, 10, 6, 4, 2, dates[3]),
            ("DBMS", "SQL", 52, 10, 5, 5, 3, dates[4])
        ], [
            ("Python", 68, dates[0]), ("Data Structures", 38, dates[1]), ("Java", 55, dates[2]), ("DBMS", 50, dates[3])
        ]),

        # Student 6: Sneha (Intermediate)
        ('student6', [
            ("Java", "Basics", 72, 10, 7, 3, 1, dates[0]),
            ("Python", "Basics", 78, 10, 8, 2, 1, dates[1]),
            ("DBMS", "SQL", 74, 10, 7, 3, 1, dates[2]),
            ("Data Structures", "Trees", 68, 10, 7, 3, 2, dates[3]),
            ("Algorithms", "Sorting", 70, 10, 7, 3, 1, dates[4])
        ], [
            ("Java", 70, dates[0]), ("Python", 75, dates[1]), ("DBMS", 72, dates[2]), ("Data Structures", 65, dates[3])
        ]),

        # Student 7: Vikram (Struggling - Low across Python and DBMS)
        ('student7', [
            ("Python", "Basics", 40, 10, 4, 6, 4, dates[0]),
            ("DBMS", "SQL", 35, 10, 3, 7, 5, dates[1]),
            ("Java", "Basics", 48, 10, 5, 5, 3, dates[2]),
            ("Data Structures", "Recursion", 30, 10, 3, 7, 6, dates[3]),
            ("DBMS", "Normalization", 38, 10, 4, 6, 4, dates[4])
        ], [
            ("Python", 42, dates[0]), ("DBMS", 36, dates[1]), ("Java", 45, dates[2]), ("Data Structures", 32, dates[3])
        ]),

        # Student 8: Kavya (Advanced)
        ('student8', [
            ("Java", "OOP", 94, 10, 9, 1, 1, dates[0]),
            ("Python", "Data Structures", 96, 10, 10, 0, 1, dates[1]),
            ("DBMS", "Transactions", 90, 10, 9, 1, 1, dates[2]),
            ("Data Structures", "Graphs", 92, 10, 9, 1, 1, dates[3]),
            ("Machine Learning", "Intro", 95, 10, 9, 1, 1, dates[4])
        ], [
            ("Java", 95, dates[0]), ("Python", 98, dates[1]), ("DBMS", 92, dates[2]), ("Machine Learning", 94, dates[3])
        ]),

        # Student 9: Aditya (Struggling in Recursion & Trees)
        ('student9', [
            ("Java", "Basics", 60, 10, 6, 4, 2, dates[0]),
            ("Data Structures", "Recursion", 32, 10, 3, 7, 5, dates[1]),
            ("Data Structures", "Trees", 38, 10, 4, 6, 4, dates[2]),
            ("Python", "Basics", 62, 10, 6, 4, 2, dates[3]),
            ("Algorithms", "Sorting", 45, 10, 4, 6, 4, dates[4])
        ], [
            ("Java", 62, dates[0]), ("Data Structures", 35, dates[1]), ("Python", 60, dates[2]), ("Algorithms", 48, dates[3])
        ]),

        # Student 10: Neha (Intermediate)
        ('student10', [
            ("Java", "OOP", 80, 10, 8, 2, 1, dates[0]),
            ("Python", "Basics", 75, 10, 7, 3, 1, dates[1]),
            ("DBMS", "SQL", 65, 10, 6, 4, 2, dates[2]),
            ("Data Structures", "Arrays", 72, 10, 7, 3, 1, dates[3]),
            ("Algorithms", "Sorting", 78, 10, 8, 2, 1, dates[4])
        ], [
            ("Java", 82, dates[0]), ("Python", 76, dates[1]), ("DBMS", 68, dates[2]), ("Data Structures", 70, dates[3])
        ])
    ]

    for uname, quizzes, assignments in perf_profiles:
        sid = student_id_map[uname]
        for subj, topic, score, total, corr, incorr, att, dt in quizzes:
            cursor.execute("""
                INSERT INTO quiz_results (student_id, subject, topic, score, total_questions, correct_answers, incorrect_answers, attempts, date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (sid, subj, topic, score, total, corr, incorr, att, dt))
            
        for subj, score, dt in assignments:
            cursor.execute("""
                INSERT INTO assignments (student_id, subject, score, date)
                VALUES (?, ?, ?, ?)
            """, (sid, subj, score, dt))

    # 5. Mark sample resources as completed for high performers
    cursor.execute("INSERT OR IGNORE INTO progress (student_id, resource_id, completed, completion_date) VALUES (?, ?, 1, ?)",
                   (student_id_map['student1'], res_id_map['Java Fundamentals Video'], dates[0]))
    cursor.execute("INSERT OR IGNORE INTO progress (student_id, resource_id, completed, completion_date) VALUES (?, ?, 1, ?)",
                   (student_id_map['student1'], res_id_map['Python Crash Course Video'], dates[1]))
    cursor.execute("INSERT OR IGNORE INTO progress (student_id, resource_id, completed, completion_date) VALUES (?, ?, 1, ?)",
                   (student_id_map['student8'], res_id_map['Java Fundamentals Video'], dates[0]))

    conn.commit()

# --- Database Access Utility Functions ---

def execute_query(query, params=()):
    """Execute a SELECT query and return all results as sqlite3.Row list."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

def execute_single_query(query, params=()):
    """Execute a SELECT query and return a single row or None."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    row = cursor.fetchone()
    conn.close()
    return row

def execute_update(query, params=()):
    """Execute an INSERT, UPDATE, or DELETE statement and return lastrowid."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

def query_to_dataframe(query, params=()):
    """Execute a query and load the dataset into a pandas DataFrame."""
    conn = get_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def save_quiz_result(student_id, subject, topic, score, total_questions, correct_answers, incorrect_answers, attempts=1):
    """Save a newly completed quiz result into database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO quiz_results (student_id, subject, topic, score, total_questions, correct_answers, incorrect_answers, attempts)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (student_id, subject, topic, score, total_questions, correct_answers, incorrect_answers, attempts))
    result_id = cursor.lastrowid
    points = 10 + int(max(0, min(20, round(float(score) / 5))))
    cursor.execute("""
        INSERT OR IGNORE INTO learning_activities
            (student_id, activity_type, source_id, title, points, score, activity_date)
        VALUES (?, 'quiz', ?, ?, ?, ?, date('now', 'localtime'))
    """, (student_id, str(result_id), f"{subject} quiz · {topic}", points, score))
    conn.commit()
    conn.close()
    return result_id

def mark_resource_completed(student_id, resource_id):
    """Mark a learning resource as completed for a given student."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO progress (student_id, resource_id, completed, completion_date)
        VALUES (?, ?, 1, CURRENT_TIMESTAMP)
        ON CONFLICT(student_id, resource_id) DO UPDATE SET completed=1, completion_date=CURRENT_TIMESTAMP
        WHERE progress.completed != 1
    """, (student_id, resource_id))
    changed = cursor.rowcount > 0
    cursor.execute("SELECT id FROM progress WHERE student_id = ? AND resource_id = ?", (student_id, resource_id))
    progress_row = cursor.fetchone()
    if changed and progress_row:
        cursor.execute("SELECT title FROM learning_resources WHERE id = ?", (resource_id,))
        resource_row = cursor.fetchone()
        title = resource_row['title'] if resource_row else 'Learning resource'
        cursor.execute("""
        INSERT OR IGNORE INTO learning_activities
            (student_id, activity_type, source_id, title, points, activity_date)
        VALUES (?, 'resource', ?, ?, 15, date('now', 'localtime'))
        """, (student_id, str(progress_row['id']), f"{title} completed"))
    conn.commit()
    conn.close()
    return progress_row['id'] if progress_row else None

def save_assignment_result(student_id, subject, score):
    """Save a newly completed practical lab assignment result into database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO assignments (student_id, subject, score, date)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    """, (student_id, subject, score))
    assignment_id = cursor.lastrowid
    cursor.execute("""
        INSERT OR IGNORE INTO learning_activities
            (student_id, activity_type, source_id, title, points, score, activity_date)
        VALUES (?, 'lab', ?, ?, 30, ?, date('now', 'localtime'))
    """, (student_id, str(assignment_id), f"{subject} practical lab", score))
    conn.commit()
    conn.close()
    return assignment_id

def log_daily_study_session(student_id):
    """Log one optional study check-in per student per local calendar day."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO learning_activities
            (student_id, activity_type, source_id, title, points, activity_date)
        VALUES (?, 'study_session', date('now', 'localtime'), 'Daily study session', 10, date('now', 'localtime'))
    """, (student_id,))
    logged = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return logged
