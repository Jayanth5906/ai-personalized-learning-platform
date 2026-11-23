"""
Personalized Recommended Learning UI Component.
Displays adaptive recommendations based on weak subjects, an All Courses Catalogue,
and an interactive study & video tutorial viewer.
"""

import streamlit as st
from utils.helpers import generate_recommendations, identify_weak_subjects
from database.database import mark_resource_completed, query_to_dataframe
from ml.predictor import predict_learning_level
from components.ui import render_page_header

# Complete Course Catalogue Data Structure
COURSES_CATALOGUE = {
    "Java": {
        "title": "Java Software Engineering Masterclass",
        "icon": "☕",
        "description": "Master Object-Oriented Programming, JVM memory management, and Java syntax.",
        "modules": [
            {
                "id": 1,
                "title": "Java Fundamentals Video",
                "topic": "Basics",
                "difficulty": "Beginner",
                "resource_type": "Video",
                "duration": "25 mins",
                "description": "Complete overview of Java syntax, variables, conditional statements, and data types.",
                "url": "https://www.youtube.com/embed/eIrMbAQSU34"
            },
            {
                "id": 2,
                "title": "Java OOP Concepts Guide",
                "topic": "OOP",
                "difficulty": "Intermediate",
                "resource_type": "Notes",
                "duration": "30 mins",
                "description": "Detailed documentation on Abstraction, Encapsulation, Inheritance, and Polymorphism.",
                "url": "https://www.youtube.com/embed/pTB0EiLXUC8"
            },
            {
                "id": 3,
                "title": "Java Beginner Practice Questions",
                "topic": "Basics",
                "difficulty": "Beginner",
                "resource_type": "Practice Questions",
                "duration": "20 mins",
                "description": "50 interactive practice questions on Java loops and control flow.",
                "url": "https://www.youtube.com/embed/eIrMbAQSU34"
            },
            {
                "id": 4,
                "title": "Java Memory Management & Garbage Collection",
                "topic": "JVM",
                "difficulty": "Advanced",
                "resource_type": "Notes",
                "duration": "40 mins",
                "description": "In-depth guide on JVM architecture, Heap vs Stack memory, and GC tuning.",
                "url": "https://www.youtube.com/embed/pTB0EiLXUC8"
            }
        ]
    },
    "Python": {
        "title": "Python Programming & Data Science",
        "icon": "🐍",
        "description": "Learn Python language fundamentals, data structures, list comprehensions, and decorators.",
        "modules": [
            {
                "id": 5,
                "title": "Python Crash Course Video",
                "topic": "Basics",
                "difficulty": "Beginner",
                "resource_type": "Video",
                "duration": "35 mins",
                "description": "Fast-paced video introduction to Python syntax, functions, and modules.",
                "url": "https://www.youtube.com/embed/rfscVS0vtbw"
            },
            {
                "id": 6,
                "title": "Python Data Structures & List Comprehensions",
                "topic": "Data Structures",
                "difficulty": "Intermediate",
                "resource_type": "Notes",
                "duration": "25 mins",
                "description": "Master lists, dicts, tuples, sets, and functional constructs.",
                "url": "https://www.youtube.com/embed/rfscVS0vtbw"
            },
            {
                "id": 7,
                "title": "Python Decorators & Generators Masterclass",
                "topic": "Advanced Topics",
                "difficulty": "Advanced",
                "resource_type": "Video",
                "duration": "45 mins",
                "description": "Deep dive into python closure mechanics, wrappers, and custom generators.",
                "url": "https://www.youtube.com/embed/rfscVS0vtbw"
            }
        ]
    },
    "DBMS": {
        "title": "DBMS & SQL Database Engineering",
        "icon": "🗄️",
        "description": "Understand Relational Databases, Normalization (1NF to 3NF), and SQL queries.",
        "modules": [
            {
                "id": 8,
                "title": "Database Fundamentals & ER Models",
                "topic": "Basics",
                "difficulty": "Beginner",
                "resource_type": "Notes",
                "duration": "30 mins",
                "description": "Comprehensive introduction to relational databases and entity relationship diagrams.",
                "url": "https://www.youtube.com/embed/GFQaEYEc8_8"
            },
            {
                "id": 9,
                "title": "DBMS Normalization Videos",
                "topic": "Normalization",
                "difficulty": "Intermediate",
                "resource_type": "Video",
                "duration": "40 mins",
                "description": "Step-by-step video breakdown of 1NF, 2NF, 3NF, and BCNF with examples.",
                "url": "https://www.youtube.com/embed/GFQaEYEc8_8"
            },
            {
                "id": 10,
                "title": "SQL Practice Quizzes & Queries",
                "topic": "SQL",
                "difficulty": "Intermediate",
                "resource_type": "Quiz",
                "duration": "25 mins",
                "description": "Practice writing complex SQL JOINs, GROUP BY, and Subqueries.",
                "url": "https://www.youtube.com/embed/GFQaEYEc8_8"
            },
            {
                "id": 11,
                "title": "Previous Exam Questions on DBMS",
                "topic": "Transactions",
                "difficulty": "Advanced",
                "resource_type": "Previous Exam Questions",
                "duration": "35 mins",
                "description": "Solved exam papers covering ACID properties, Indexing, and Concurrency Control.",
                "url": "https://www.youtube.com/embed/GFQaEYEc8_8"
            }
        ]
    },
    "Data Structures": {
        "title": "Data Structures & Trees Core",
        "icon": "🌲",
        "description": "Linear and non-linear data structures: Arrays, Linked Lists, Recursion, Trees, and Graphs.",
        "modules": [
            {
                "id": 12,
                "title": "Arrays and Linked Lists Basics",
                "topic": "Arrays",
                "difficulty": "Beginner",
                "resource_type": "Notes",
                "duration": "20 mins",
                "description": "Linear data structures visual guide with array vs linked list comparison.",
                "url": "https://www.youtube.com/embed/ngCos392W4w"
            },
            {
                "id": 13,
                "title": "Recursion Fundamentals & Visualizer",
                "topic": "Recursion",
                "difficulty": "Beginner",
                "resource_type": "Video",
                "duration": "30 mins",
                "description": "Step-by-step video explaining call stacks, base cases, and recursive trees.",
                "url": "https://www.youtube.com/embed/ngCos392W4w"
            },
            {
                "id": 14,
                "title": "Binary Trees & BST Masterclass",
                "topic": "Trees",
                "difficulty": "Intermediate",
                "resource_type": "Video",
                "duration": "45 mins",
                "description": "Interactive video explaining binary tree traversals (Inorder, Preorder, Postorder) and BST ops.",
                "url": "https://www.youtube.com/embed/fAAZixBzVSc"
            },
            {
                "id": 15,
                "title": "Graph Algorithms & Shortest Path Notes",
                "topic": "Graphs",
                "difficulty": "Advanced",
                "resource_type": "Notes",
                "duration": "50 mins",
                "description": "In-depth analysis of BFS, DFS, Dijkstra's algorithm, and Minimum Spanning Trees.",
                "url": "https://www.youtube.com/embed/fAAZixBzVSc"
            }
        ]
    },
    "Algorithms": {
        "title": "Algorithm Design & Complexity",
        "icon": "⚡",
        "description": "Learn sorting, searching, asymptotic notation, and Dynamic Programming.",
        "modules": [
            {
                "id": 16,
                "title": "Sorting & Searching Algorithms Video",
                "topic": "Sorting",
                "difficulty": "Beginner",
                "resource_type": "Video",
                "duration": "30 mins",
                "description": "Visual animations of Bubble Sort, Merge Sort, and Binary Search.",
                "url": "https://www.youtube.com/embed/ngCos392W4w"
            },
            {
                "id": 17,
                "title": "Dynamic Programming for Beginners",
                "topic": "DP",
                "difficulty": "Advanced",
                "resource_type": "Notes",
                "duration": "45 mins",
                "description": "Overlapping subproblems, memoization vs tabulation with classic examples.",
                "url": "https://www.youtube.com/embed/ngCos392W4w"
            }
        ]
    },
    "Machine Learning": {
        "title": "Machine Learning & AI Foundations",
        "icon": "🤖",
        "description": "Supervised learning, classification algorithms, and Random Forest models.",
        "modules": [
            {
                "id": 18,
                "title": "Introduction to Machine Learning Concepts",
                "topic": "Intro",
                "difficulty": "Beginner",
                "resource_type": "Video",
                "duration": "25 mins",
                "description": "Supervised vs Unsupervised learning overview for beginners.",
                "url": "https://www.youtube.com/embed/eIrMbAQSU34"
            },
            {
                "id": 19,
                "title": "Scikit-Learn Random Forest Tutorial",
                "topic": "Ensemble",
                "difficulty": "Intermediate",
                "resource_type": "Notes",
                "duration": "35 mins",
                "description": "Building decision tree ensembles using Python Scikit-Learn.",
                "url": "https://www.youtube.com/embed/eIrMbAQSU34"
            }
        ]
    }
}

# Detailed Study Material Content Library for Interactive Viewer
RESOURCE_CONTENT_LIBRARY = {
    "Java Fundamentals Video": {
        "video_url": "https://www.youtube.com/embed/eIrMbAQSU34",
        "notes": """
### ☕ Java Fundamentals Study Notes

#### 1. Core Syntax & Data Types
Java is a strongly-typed, object-oriented language compiled to bytecode and executed on the Java Virtual Machine (JVM).

* **Primitives:** `byte`, `short`, `int`, `long`, `float`, `double`, `char`, `boolean`
* **Reference Types:** Class instances, Arrays, Interfaces

```java
public class HelloWorld {
    public static void main(String[] args) {
        int studentScore = 85;
        double gpa = 3.8;
        boolean isPassed = studentScore >= 50;
        
        System.out.println("Score: " + studentScore + " | Passed: " + isPassed);
    }
}
```
        """,
        "practice": "Write a Java loop that prints all even numbers between 1 and 20."
    },
    "Java OOP Concepts Guide": {
        "video_url": "https://www.youtube.com/embed/pTB0EiLXUC8",
        "notes": """
### 🧩 Java Object-Oriented Programming (OOP) Master Guide

```java
class Student {
    private String name;
    private int score;

    public Student(String name, int score) {
        this.name = name;
        this.score = score;
    }

    public int getScore() { return score; }
}
```
        """,
        "practice": "Create a `Shape` interface with a method `double calculateArea()` and implement it in a `Circle` class."
    },
    "DBMS Normalization Videos": {
        "video_url": "https://www.youtube.com/embed/GFQaEYEc8_8",
        "notes": """
### 🗄️ Database Normalization & Integrity Guide

```sql
-- Normalized 3NF Tables
CREATE TABLE Students (
    student_id INT PRIMARY KEY,
    name VARCHAR(100),
    dept_id INT FOREIGN KEY REFERENCES Departments(dept_id)
);
```
        """,
        "practice": "Identify the functional dependency causing a 3NF violation in `Book(ISBN, Title, Author_ID, Author_Email)`."
    },
    "Dynamic Programming for Beginners": {
        "video_url": "https://www.youtube.com/embed/ngCos392W4w",
        "notes": """
### ⚡ Dynamic Programming Masterclass

```python
# Memoized Fibonacci (Top-Down DP)
def fib(n, memo={}):
    if n <= 1:
        return n
    if n not in memo:
        memo[n] = fib(n - 1, memo) + fib(n - 2, memo)
    return memo[n]

print(fib(50)) # Output: 12586269025
```
        """,
        "practice": "Implement dynamic programming to solve the 0/1 Knapsack Problem."
    },
    "Recursion Fundamentals & Visualizer": {
        "video_url": "https://www.youtube.com/embed/ngCos392W4w",
        "notes": """
### 🔄 Recursion & Call Stack Execution Guide

```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```
        """,
        "practice": "Write a recursive Python function `sum_digits(n)` that calculates digit sum of n."
    },
    "Python Crash Course Video": {
        "video_url": "https://www.youtube.com/embed/rfscVS0vtbw",
        "notes": """
### 🐍 Python Core Programming Guide

```python
scores = [92, 42, 85, 70]
passing = [s for s in scores if s >= 50]
print("Passing Scores:", passing)
```
        """,
        "practice": "Write a list comprehension that extracts all words starting with a vowel from a sentence."
    },
    "Binary Trees & BST Masterclass": {
        "video_url": "https://www.youtube.com/embed/fAAZixBzVSc",
        "notes": """
### 🌳 Binary Search Trees (BST) & Traversals

```python
def inorder(root):
    if root:
        inorder(root.left)
        print(root.val)
        inorder(root.right)
```
        """,
        "practice": "What is the output of performing an Inorder traversal on a BST containing [15, 10, 20]?"
    }
}

def render_interactive_material_viewer(resource, student_id):
    """Render full interactive study material content viewer when student clicks 'Start Learning'."""
    res_title = resource['title']
    res_subject = resource.get('subject', 'Computer Science')
    res_diff = resource.get('difficulty', 'Beginner')
    res_desc = resource.get('description', 'Study resource content.')
    raw_url = resource.get('url', '')

    # Fallback map to ensure NO example.com URLs ever show up
    default_video_map = {
        "Java": "https://www.youtube.com/embed/eIrMbAQSU34",
        "Python": "https://www.youtube.com/embed/rfscVS0vtbw",
        "DBMS": "https://www.youtube.com/embed/GFQaEYEc8_8",
        "Data Structures": "https://www.youtube.com/embed/fAAZixBzVSc",
        "Algorithms": "https://www.youtube.com/embed/ngCos392W4w",
        "Machine Learning": "https://www.youtube.com/embed/eIrMbAQSU34"
    }

    if not raw_url or "example.com" in raw_url:
        video_link = default_video_map.get(res_subject, "https://www.youtube.com/embed/ngCos392W4w")
    else:
        video_link = raw_url

    render_page_header("LEARNING RESOURCE", res_title, res_desc, "📖")

    content_info = RESOURCE_CONTENT_LIBRARY.get(res_title, {
        "video_url": video_link,
        "notes": f"### 📚 Interactive Study Notes: {res_title}\n\nThis study module covers fundamental concepts for **{res_subject}**.\n\n#### Key Learning Objectives:\n1. Master core principles of this module.\n2. Solve practice exercises to reinforce understanding.\n3. Prepare for upcoming practice quizzes.",
        "practice": f"Review key principles of {res_title} and solve practice exercises."
    })

    # Ensure video_url in content_info is valid
    if "example.com" in content_info.get("video_url", ""):
        content_info["video_url"] = video_link

    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <span style="background: #93C5FD; color: #1E3A8A; padding: 4px 12px; border-radius: 12px; font-weight: 700; font-size: 12px;">{res_subject}</span>
            <span style="background: #FDE68A; color: #92400E; padding: 4px 12px; border-radius: 12px; font-weight: 700; font-size: 12px; margin-left: 6px;">{res_diff}</span>
            <h2 style="margin: 10px 0 4px 0; color: white;">📖 Currently Learning: {res_title}</h2>
            <p style="margin: 0; color: #DBEAFE; font-size: 14px;">{res_desc}</p>
        </div>
    """, unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("⬅️ Back to Resources", key="btn_close_viewer"):
            st.session_state['active_learning_resource'] = None
            st.rerun()

    tab_video, tab_notes, tab_practice = st.tabs(["🎥 Video Lesson", "📝 Detailed Notes & Code", "✏️ Practice Exercises"])

    with tab_video:
        st.subheader("📹 Embedded Video Tutorial")
        final_embed_url = content_info.get("video_url", video_link)
        st.markdown(f"""
            <iframe width="100%" height="480" src="{final_embed_url}" title="Video Tutorial Player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen style="border-radius: 10px; border: 1px solid #E2E8F0;"></iframe>
        """, unsafe_allow_html=True)

    with tab_notes:
        st.markdown(content_info.get("notes", "Study notes loaded."))

    with tab_practice:
        st.subheader("💡 Knowledge Check & Exercises")
        st.markdown(f"**Exercise Prompt:** {content_info.get('practice', 'Complete exercises.')}")
        student_code = st.text_area("Write your solution or code here for practice:", height=150, placeholder="Type your answer or code here...")
        if st.button("Submit Answer for Assessment", key="btn_sub_practice"):
            st.success("Great job practicing! Keep up the good momentum.")

    st.markdown("---")

    c_comp1, c_comp2 = st.columns([2, 1])
    with c_comp1:
        st.info("Finished reviewing this material? Click 'Mark as Completed' to record your progress and update recommendations!")
    with c_comp2:
        res_id = resource.get('id', 1)
        if st.button("Mark Completed & Update AI ✅", key=f"comp_in_viewer_{res_id}"):
            mark_resource_completed(student_id, res_id)
            st.success(f"Completed '{res_title}'! Updating recommendations...")
            st.session_state['active_learning_resource'] = None
            st.rerun()

def render_recommendations_page(student_id):
    """Render full Recommended Learning Resources page for a student."""
    
    # Check if an active resource is currently selected for learning
    active_resource = st.session_state.get('active_learning_resource')
    if active_resource:
        render_interactive_material_viewer(active_resource, student_id)
        return

    render_page_header(
        "PERSONALIZED LEARNING",
        "Learning resource hub",
        "Explore recommendations shaped by your progress or browse the full course catalogue.",
        "📚",
    )

    pred_res = predict_learning_level(student_id=student_id)
    learning_level = pred_res['learning_level']
    weak_subjects = identify_weak_subjects(student_id)

    tab1, tab2 = st.tabs(["🎯 AI Personalized Recommendations", "📹 All Available Courses & Video Catalogue"])

    with tab1:
        # Info summary bar
        st.markdown(f"""
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 16px; border-radius: 8px; margin-bottom: 24px;">
                <span style="font-size: 14px; font-weight: 600; color: #1E293B;">Target Learning Level:</span> 
                <span style="background: #DBEAFE; color: #1E40AF; padding: 3px 10px; border-radius: 12px; font-weight: 700; font-size: 13px;">{learning_level}</span>
                &nbsp;&nbsp;|&nbsp;&nbsp;
                <span style="font-size: 14px; font-weight: 600; color: #1E293B;">Focus Subjects (Weak):</span> 
                <span style="color: #EF4444; font-weight: 700;">{", ".join(weak_subjects) if weak_subjects else "None (All subjects strong!)"}</span>
            </div>
        """, unsafe_allow_html=True)

        recommendations = generate_recommendations(student_id)

        if not recommendations:
            st.success("🎉 You have completed all recommended resources for your current learning path! Take a practice quiz to test your updated skills.")
        else:
            st.subheader(f"Recommended Resources for You ({len(recommendations)})")

            for idx in range(0, len(recommendations), 2):
                cols = st.columns(2)
                for c_idx in range(2):
                    if idx + c_idx < len(recommendations):
                        rec = recommendations[idx + c_idx]
                        with cols[c_idx]:
                            st.markdown(f"""
                                <div style="background: white; border: 1px solid #E2E8F0; border-radius: 10px; padding: 20px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.04);">
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <span style="background: #E0E7FF; color: #3730A3; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 700;">{rec['subject']}</span>
                                        <span style="background: #FEF3C7; color: #92400E; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 700;">{rec['difficulty']}</span>
                                    </div>
                                    <h3 style="margin: 12px 0 6px 0; font-size: 18px; color: #1E293B;">{rec['title']}</h3>
                                    <p style="font-size: 14px; color: #64748B; margin-bottom: 12px;">{rec['description']}</p>
                                    <div style="margin-bottom: 10px;">
                                        <span style="font-size: 12px; color: #475569;"><strong>Topic:</strong> {rec['topic']}</span> &nbsp;•&nbsp; 
                                        <span style="font-size: 12px; color: #475569;"><strong>Format:</strong> {rec['resource_type']}</span>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            btn_col1, btn_col2 = st.columns([1, 1])
                            with btn_col1:
                                if st.button(f"Start Learning 🚀", key=f"rec_start_{rec['id']}"):
                                    st.session_state['active_learning_resource'] = rec
                                    st.rerun()
                            with btn_col2:
                                if st.button("Mark Completed ✅", key=f"rec_comp_{rec['id']}"):
                                    mark_resource_completed(student_id, rec['id'])
                                    st.success(f"Marked '{rec['title']}' as completed! Updating recommendations...")
                                    st.rerun()

    with tab2:
        st.subheader("📹 All Available Video Courses & Learning Catalogue")
        st.caption("Total 6 Core Courses | 19 Video Modules & Reading Resources Available")

        # Filter by course dropdown
        course_keys = list(COURSES_CATALOGUE.keys())
        selected_course = st.selectbox("Filter by Course Subject", ["All Courses (6 Core Tracks)"] + course_keys)

        display_courses = course_keys if selected_course == "All Courses (6 Core Tracks)" else [selected_course]

        for ckey in display_courses:
            cdata = COURSES_CATALOGUE[ckey]
            st.markdown(f"""
                <div style="background: white; border: 1px solid #E2E8F0; border-left: 5px solid #3B82F6; border-radius: 8px; padding: 16px; margin-top: 16px; margin-bottom: 12px;">
                    <h3 style="margin:0; color:#1E293B;">{cdata['icon']} {cdata['title']} ({len(cdata['modules'])} Modules)</h3>
                    <p style="margin:4px 0 0 0; color:#64748B; font-size:14px;">{cdata['description']}</p>
                </div>
            """, unsafe_allow_html=True)

            mod_cols = st.columns(2)
            for idx, mod in enumerate(cdata['modules']):
                with mod_cols[idx % 2]:
                    st.markdown(f"""
                        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px; margin-bottom: 10px;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span style="background: #DBEAFE; color:#1E40AF; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 700;">{mod['resource_type']}</span>
                                <span style="font-size: 12px; color: #64748B; font-weight:600;">⏱️ {mod['duration']}</span>
                            </div>
                            <h4 style="margin: 8px 0 4px 0; font-size: 15px; color:#1E293B;">{mod['title']}</h4>
                            <p style="margin:0; font-size:13px; color:#475569;">{mod['description']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Watch Video & Study 🎥", key=f"cat_start_{ckey}_{mod['id']}"):
                        st.session_state['active_learning_resource'] = {
                            'id': mod['id'],
                            'title': mod['title'],
                            'subject': ckey,
                            'topic': mod['topic'],
                            'difficulty': mod['difficulty'],
                            'description': mod['description'],
                            'url': mod['url']
                        }
                        st.rerun()
