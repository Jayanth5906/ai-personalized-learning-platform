# AI-POWERED PERSONALIZED LEARNING PLATFORM

An intelligent, real-time adaptive learning web application built with **Python**, **Streamlit**, **Scikit-learn**, **SQLite**, **Pandas**, and **Plotly**. The platform analyzes student academic performance (quiz scores, assignment marks, study time, attempts, completed activities) to classify students into learning levels, detect strong/weak subjects, generate personalized learning recommendations, provide an AI Academic Tutor, and equip teachers with comprehensive class-level analytics.

---

## 1. PROJECT OBJECTIVE

The primary objective of this platform is to harness Machine Learning and Artificial Intelligence to personalize learning at scale:
- **For Students:** Automatically identify strengths and weaknesses, predict learning levels (`Beginner`, `Intermediate`, `Advanced`), dynamically recommend uncompleted study materials, provide adaptive AI Tutor support, and track historical progress.
- **For Teachers:** Detect struggling/at-risk students early (`Needs Improvement`), pinpoint difficult topics across the cohort (e.g. Recursion 70% failure rate), visualize learning-level distribution, and provide actionable teaching recommendations.

---

## 2. TECHNOLOGY STACK

- **Core Language:** Python 3.10+
- **Frontend / Application Framework:** Streamlit
- **Machine Learning:** Scikit-learn (Random Forest Classifier), Joblib
- **Data Processing:** Pandas, NumPy
- **Database:** SQLite 3
- **Data Visualization:** Plotly Express & Plotly Graph Objects
- **Configuration & Environment:** Python-dotenv

---

## 3. KEY FEATURES

### 👤 Student Workspace
1. **Interactive Dashboard:** Real-time metrics for Overall Score, ML Learning Level (with confidence %), Completed Quizzes, and Study Progress.
2. **Weak & Strong Subject Detection:** Configurable performance thresholding (Strong $\ge 75\%$, Average $50-74\%$, Weak $< 50\%$).
3. **Personalized Learning Recommendation Engine:** Dynamically generates resource cards matching weak subjects and learning level while filtering out already completed materials.
4. **AI Academic Tutor:** Chat interface adapting explanation depth (Beginner simple language vs Advanced deep technical details) with fallback to built-in pedagogical responder.
5. **Interactive Practice Quiz System:** Live quiz testing across subjects (Java, Python, DBMS, Data Structures, Algorithms, Machine Learning). Instant grading, detailed explanations, and auto-updating SQLite DB & ML feature state.
6. **My Performance Analytics:** Plotly weekly progress trend lines, subject proficiency radar charts, and quiz logs.
7. **Learning Goals & Achievements:** Earn XP from quizzes, assignments, practical labs, and completed resources; build daily streaks with activity or an optional study check-in; and unlock progress badges.

### 🎓 Teacher Workspace
1. **Class Overview Dashboard:** Aggregate metrics for total students, class average score, top performers, and at-risk student count.
2. **Learning-Level Distribution:** Interactive Plotly pie chart showing Random Forest classification split across the cohort.
3. **Early Identification of Struggling Students:** AI-driven detection marking students as `Needs Improvement` with explicit diagnosis notes (low score, high attempts, insufficient study time).
4. **Difficult Topic Detection:** Class-wide topic failure rate calculation (e.g., Recursion struggle rate $\ge 70\%$) with actionable revision session prompts.
5. **Individual Student Inspection:** Deep-dive modal/view for inspecting any student's complete profile, quiz history, weak subjects, recommendations, and risk status.
6. **ML Classifier Evaluation:** Live confusion matrix, accuracy score, and feature importance bar chart with one-click live retraining.

---

## 4. SYSTEM WORKFLOW

```text
Student Login
     │
     ▼
Collect Performance Data (Quizzes, Assignments, Study Time, Attempts)
     │
     ▼
Data Preprocessing & Feature Extraction
     │
     ▼
Random Forest Classifier ──► Predict Learning Level (Beginner / Intermediate / Advanced)
     │
     ▼
Detect Weak (<50%) and Strong (≥75%) Subjects
     │
     ▼
Personalized Recommendation Engine (Filters Completed Resources)
     │
     ▼
Practice Quiz System / AI Tutor Interaction
     │
     ▼
Save Results to SQLite DB ──► Update ML State & Recalculate Recommendations

─────────────────────────────────────────────────────────────────────────────

Teacher Login
     │
     ▼
Teacher Class Dashboard
     │
     ▼
Class Analytics & Learning Level Distribution
     │
     ▼
Identify Struggling Students (Needs Improvement) & Difficult Topics
     │
     ▼
Targeted Academic Support & Revision Sessions
```

---

## 5. PROJECT STRUCTURE

```text
ai driven personalized education platform/
├── app.py                      # Main Streamlit application entry point & router
├── requirements.txt            # Project dependency specifications
├── README.md                   # Technical documentation
├── .env.example                # Template for optional API keys
├── database.db                 # SQLite database file (created automatically)
├── database/
│   ├── __init__.py
│   ├── schema.py               # Table creation queries
│   └── database.py             # SQLite connection management & seeding logic
├── ml/
│   ├── __init__.py
│   ├── model.py                # Feature preprocessing and extraction
│   ├── train_model.py          # Random Forest training & evaluation
│   └── predictor.py            # Model inference engine
├── components/
│   ├── __init__.py
│   ├── student_dashboard.py    # Student metrics, badges & charts
│   ├── teacher_dashboard.py    # Teacher overview, risk flags & class charts
│   ├── ai_tutor.py             # Adaptive chat interface UI
│   ├── recommendations.py      # Resource recommendation cards & completion tracking
│   ├── quiz.py                 # Interactive practice quiz system
│   ├── analytics.py            # Curriculum analytics & ML model metrics
│   ├── my_performance.py       # Performance monitoring & Plotly trends
│   └── student_details.py      # Individual student inspector for teachers
├── data/
│   ├── students.csv            # Exported student dataset
│   ├── quiz_results.csv        # Exported quiz historical log
│   └── learning_resources.csv  # Learning resources catalogue
├── utils/
│   ├── __init__.py
│   ├── helpers.py              # Business logic (recommendations, risk analysis, topic metrics)
│   └── authentication.py       # User authentication and Streamlit session state
└── models/
    └── student_classifier.pkl  # Trained Random Forest model binary
```

---

## 6. INSTALLATION & SETUP

### Step 1: Clone or Navigate to Directory
```bash
cd "c:/Users/kartik/Desktop/ai driven personalized education platform"
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Optional Environment Variables (Optional)
Copy `.env.example` to `.env` if you wish to configure Gemini or OpenAI API keys:
```bash
cp .env.example .env
```
*(If no API key is provided, the platform automatically utilizes its built-in pedagogical offline responder).*

---

## 7. HOW TO RUN

Launch the application using the Python Streamlit module:

```bash
py -m streamlit run app.py
```
*(or `streamlit run app.py` if Python Scripts is added to your system PATH).*

Open your browser at `http://localhost:8501`.

---

## 8. SAMPLE LOGIN CREDENTIALS

The platform initializes with realistic pre-populated data for immediate testing:

### 👤 Student Accounts
- **Username:** `student1` | **Password:** `student123` (Aarav Patel - Advanced)
- **Username:** `student2` | **Password:** `student123` (Ananya Gupta - Intermediate)
- **Username:** `student3` | **Password:** `student123` (Rahul Sharma - Struggling / Beginner)
- **Username:** `student4` | **Password:** `student123` (Priya Verma - Weak in DBMS)
- **Username:** `student5` | **Password:** `student123` (Rohan Mehta - Weak in Recursion)

### 🎓 Teacher Accounts
- **Username:** `teacher1` | **Password:** `teacher123` (Dr. Rajesh Sharma)
- **Username:** `teacher2` | **Password:** `teacher123` (Prof. Sunita Rao)

---

## 9. MACHINE LEARNING MODEL DETAILS

- **Algorithm:** `RandomForestClassifier` (100 estimators, balanced class weights).
- **Input Features:**
  1. `avg_quiz_score`: Mean quiz percentage
  2. `avg_assignment_score`: Mean assignment score
  3. `study_time`: Weekly logged study hours
  4. `avg_attempts`: Average attempts per quiz
  5. `completed_activities`: Total completed learning modules
  6. `overall_subject_perf`: Composite score weighted index
- **Target Output Classes:** `Beginner`, `Intermediate`, `Advanced`.
- **Training Pipeline:** Located in `ml/train_model.py`. Trains on synthetic feature vectors + real DB samples, achieving $>90\%$ evaluation accuracy.
- **Model Storage:** Saved to `models/student_classifier.pkl` via Joblib.

---

## 10. DATABASE SCHEMA

SQLite database (`database.db`) manages 8 core tables:
- `users`: User authentication profiles (`id`, `username`, `password`, `role`, `name`)
- `students`: Student profile details (`id`, `user_id`, `name`, `learning_level`, `study_time`)
- `subjects`: Curriculum subjects (`id`, `subject_name`)
- `quiz_results`: Quiz attempts history (`id`, `student_id`, `subject`, `topic`, `score`, `total_questions`, `correct_answers`, `incorrect_answers`, `attempts`, `date`)
- `assignments`: Assignment scores (`id`, `student_id`, `subject`, `score`, `date`)
- `learning_resources`: Content catalogue (`id`, `title`, `subject`, `topic`, `difficulty`, `resource_type`, `description`, `url`)
- `progress`: Module completion tracking (`id`, `student_id`, `resource_id`, `completed`, `completion_date`)
- `learning_activities`: XP and streak history for quizzes, assignments, labs, completed resources, and daily study check-ins.

---

## 11. SIX DEMONSTRATED USE CASES

1. **Use Case 1: Personalized Learning Path:** Student logs in, takes a Java quiz, scores $45\%$, ML classifies as `Beginner`, weak subject Java detected $\rightarrow$ system recommends *Java Basics* & *OOP Concepts*.
2. **Use Case 2: AI Tutor Assistance:** Student asks *"Explain Binary Trees with an example"* $\rightarrow$ AI Tutor formats response according to student's level (Beginner vs Advanced) with code examples and practice questions.
3. **Use Case 3: Early Identification of Struggling Students:** Teacher dashboard flags Rahul Sharma with status `Needs Improvement` due to low score ($40.6\%$), high incorrect attempts, and low study time ($4.5$ hrs).
4. **Use Case 4: Dynamic Recommendations Filtering:** Student performs well in Python but poorly in DBMS $\rightarrow$ system recommends *DBMS Normalization* videos and *SQL Practice Quizzes* while automatically filtering out completed Python items.
5. **Use Case 5: Performance Monitoring:** Student inspects "My Performance" tab $\rightarrow$ views Plotly trend lines showing score improvements over time.
6. **Use Case 6: Teacher Class Analytics:** Teacher opens analytics $\rightarrow$ discovers $70\%$ of class struggles with *Recursion* $\rightarrow$ system generates teacher recommendation *"Consider conducting a revision session on Recursion"*.

---

## 12. FUTURE ENHANCEMENTS

- Automated LMS integrations (Moodle / Canvas API connectors).
- Deep reinforcement learning for continuous recommendation policy optimization.
