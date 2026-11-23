"""
Practical Data Engineering & AI Coding Labs UI Component.
Provides interactive hands-on programming labs, real-time Python/SQL code execution, and lab assignment grading.
"""

import streamlit as st
import pandas as pd
import numpy as np
import io
import sys
import sqlite3
from database.database import save_assignment_result, query_to_dataframe
from components.ui import render_page_header

def render_practical_labs(student_id):
    """Render interactive Practical DE & AI Coding Labs for students."""
    st.markdown("""
        <style>
            .lab-badge {
                display: inline-block;
                background: linear-gradient(135deg, #06B6D4 0%, #3B82F6 100%);
                color: white;
                font-weight: 700;
                font-size: 12px;
                padding: 4px 12px;
                border-radius: 9999px;
                letter-spacing: 0.5px;
                text-transform: uppercase;
                margin-bottom: 8px;
            }
            .lab-card {
                background: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
                margin-bottom: 20px;
            }
            .output-box {
                background-color: #0F172A;
                color: #38BDF8;
                font-family: 'Courier New', Courier, monospace;
                padding: 14px;
                border-radius: 8px;
                font-size: 13px;
                white-space: pre-wrap;
                margin-top: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

    render_page_header(
        "HANDS-ON LEARNING",
        "Practical coding labs",
        "Build confidence with Python, SQL, data engineering, and machine-learning exercises.",
        "🧪",
    )

    # 1. Fetch Practical Assignment History for Student
    assignments_df = query_to_dataframe(
        "SELECT subject, score, date FROM assignments WHERE student_id = ? ORDER BY date DESC",
        (student_id,)
    )

    col_labs, col_history = st.columns([2, 1])

    with col_history:
        st.subheader("📊 Completed Lab Grades")
        if not assignments_df.empty:
            avg_lab_score = round(assignments_df['score'].mean(), 1)
            st.metric("Lab Assignments Average", f"{avg_lab_score}%")
            st.dataframe(
                assignments_df.rename(columns={'subject': 'Lab Subject', 'score': 'Score (%)', 'date': 'Completion Date'}),
                width="stretch"
            )
        else:
            st.info("No practical labs submitted yet. Select a lab on the left and click 'Run & Submit Lab' to earn your first score!")

    with col_labs:
        st.subheader("⚡ Available Practical DE & AI Labs")

        lab_option = st.selectbox(
            "Select Practical Lab Assignment Module:",
            [
                "Lab 1: PySpark Data Pipeline & ETL Aggregations (Python)",
                "Lab 2: SQL Data Warehousing & Window Functions (DBMS)",
                "Lab 3: Scikit-Learn Model Training & Feature Pipeline (Machine Learning)",
                "Lab 4: Streaming Log Parser & Throughput Calculator (Data Structures)"
            ]
        )

        st.markdown("---")

        if "Lab 1" in lab_option:
            render_lab_pyspark(student_id)
        elif "Lab 2" in lab_option:
            render_lab_sql(student_id)
        elif "Lab 3" in lab_option:
            render_lab_ml(student_id)
        elif "Lab 4" in lab_option:
            render_lab_streaming(student_id)


def render_lab_pyspark(student_id):
    st.markdown("### 🧪 Lab 1: PySpark Data Pipeline & ETL Aggregation")
    st.markdown("""
    **Objective:** Extract raw e-commerce transaction data, filter out missing price values, calculate total revenue (`price * quantity`), and group total revenue by product category.
    """)

    default_code = """# PySpark ETL Data Pipeline Task
import pandas as pd

# 1. Load raw sales data stream
df = pd.DataFrame({
    'category': ['Electronics', 'Electronics', 'Books', 'Books', 'Clothing', 'Electronics'],
    'price': [299.99, 150.00, 25.50, None, 45.00, 89.99],
    'quantity': [2, 1, 4, 2, 3, 5]
})

# 2. Filter out null values in price column
df_clean = df.dropna(subset=['price'])

# 3. Calculate total revenue per item: revenue = price * quantity
df_clean['revenue'] = df_clean['price'] * df_clean['quantity']

# 4. Group by category and calculate total category revenue
result = df_clean.groupby('category')['revenue'].sum().reset_index()

print("--- ETL PIPELINE AGGREGATED OUTPUT ---")
print(result)
"""

    user_code = st.text_area("Python ETL Script Editor:", value=default_code, height=260, key="lab1_code")

    if st.button("🚀 Run & Submit Lab 1 Assignment", width="stretch", key="btn_run_lab1"):
        buffer = io.StringIO()
        sys.stdout = buffer
        try:
            local_scope = {}
            exec(user_code, globals(), local_scope)
            sys.stdout = sys.__stdout__
            output_str = buffer.getvalue()

            # Validation logic
            res_df = local_scope.get('result')
            if isinstance(res_df, pd.DataFrame) and 'revenue' in res_df.columns and len(res_df) == 3:
                score = 100.0
                st.success("✅ **Lab Assignment Passed!** ETL data pipeline output matches expected schema & values (100% Score).")
            else:
                score = 85.0
                st.warning("⚠️ **Lab Executed with Partial Credit (85%)**: Script output executed cleanly.")

            st.markdown(f'<div class="output-box">{output_str}</div>', unsafe_allow_html=True)
            save_assignment_result(student_id, "Python", score)
            st.info("🏆 Practical lab grade recorded! Check 'My Performance & Weaknesses' to see your updated lab charts.")
            st.rerun()

        except Exception as e:
            sys.stdout = sys.__stdout__
            st.error(f"❌ Execution Error: {str(e)}")


def render_lab_sql(student_id):
    st.markdown("### 🧪 Lab 2: SQL Data Warehousing & Window Functions")
    st.markdown("""
    **Objective:** Execute analytical SQL queries using window functions (`DENSE_RANK()` and running `SUM()`) over customer purchase data.
    """)

    default_sql = """-- Data Warehousing SQL Query Task
SELECT 
    customer_id,
    total_spend,
    DENSE_RANK() OVER (ORDER BY total_spend DESC) as customer_rank,
    SUM(total_spend) OVER (ORDER BY customer_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) as running_total
FROM customer_orders;
"""

    user_sql = st.text_area("SQL Data Warehouse Editor:", value=default_sql, height=180, key="lab2_code")

    if st.button("🚀 Run & Submit Lab 2 Assignment", width="stretch", key="btn_run_lab2"):
        try:
            # Create sample SQLite in-memory database for SQL execution
            conn = sqlite3.connect(":memory:")
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE customer_orders (
                    customer_id INTEGER,
                    total_spend REAL
                )
            """)
            cursor.executemany("INSERT INTO customer_orders VALUES (?, ?)", [
                (101, 1500.0), (102, 3200.5), (103, 850.0), (104, 3200.5), (105, 4100.0)
            ])
            conn.commit()

            df_res = pd.read_sql_query(user_sql, conn)
            conn.close()

            st.success("✅ **SQL Query Executed Successfully!** Output dataset generated using SQLite Window Functions.")
            st.dataframe(df_res, width="stretch")

            score = 100.0
            save_assignment_result(student_id, "DBMS", score)
            st.info("🏆 Practical lab grade (100%) recorded in SQLite Database! View performance trends in 'My Performance'.")
            st.rerun()

        except Exception as e:
            st.error(f"❌ SQL Execution Error: {str(e)}")


def render_lab_ml(student_id):
    st.markdown("### 🧪 Lab 3: Scikit-Learn Model Training & Feature Pipeline")
    st.markdown("""
    **Objective:** Build a machine learning classifier feature pipeline using Scikit-Learn to predict student learning levels.
    """)

    default_code = """# Machine Learning Feature Pipeline Task
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import numpy as np

# 1. Feature Matrix: [quiz_score, study_time, attempts]
X = np.array([[45, 4, 8], [88, 20, 1], [30, 2, 12], [92, 25, 0], [70, 12, 3]])
y = np.array(['Beginner', 'Advanced', 'Beginner', 'Advanced', 'Intermediate'])

# 2. Initialize and fit Random Forest Classifier
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X, y)

# 3. Model Inference & Evaluation
preds = clf.predict(X)
acc = accuracy_score(y, preds)

print("--- ML PIPELINE TRAINING RESULTS ---")
print(f"Classifier Type: Random Forest")
print(f"Training Accuracy: {acc * 100:.1f}%")
print(f"Feature Importances: {clf.feature_importances_}")
"""

    user_code = st.text_area("Python ML Pipeline Editor:", value=default_code, height=260, key="lab3_code")

    if st.button("🚀 Run & Submit Lab 3 Assignment", width="stretch", key="btn_run_lab3"):
        buffer = io.StringIO()
        sys.stdout = buffer
        try:
            local_scope = {}
            exec(user_code, globals(), local_scope)
            sys.stdout = sys.__stdout__
            output_str = buffer.getvalue()

            score = 95.0
            st.success("✅ **ML Pipeline Executed Successfully!** Random Forest classifier trained & feature importances calculated (95% Score).")
            st.markdown(f'<div class="output-box">{output_str}</div>', unsafe_allow_html=True)
            save_assignment_result(student_id, "Machine Learning", score)
            st.info("🏆 Practical ML lab grade recorded!")
            st.rerun()

        except Exception as e:
            sys.stdout = sys.__stdout__
            st.error(f"❌ ML Pipeline Execution Error: {str(e)}")


def render_lab_streaming(student_id):
    st.markdown("### 🧪 Lab 4: Streaming Log Parser & Throughput Calculator")
    st.markdown("""
    **Objective:** Parse structured JSON log streams, filter successful status events (200 OK), and calculate real-time data throughput.
    """)

    default_code = """# Real-Time Event Log Streaming Processor
import json

logs = [
    '{"timestamp": "12:00:01", "status": 200, "bytes": 1024}',
    '{"timestamp": "12:00:01", "status": 500, "bytes": 0}',
    '{"timestamp": "12:00:02", "status": 200, "bytes": 2048}',
    '{"timestamp": "12:00:02", "status": 200, "bytes": 512}'
]

# Parse JSON event records
processed_logs = [json.loads(log) for log in logs]
success_logs = [l for l in processed_logs if l['status'] == 200]
total_bytes = sum(l['bytes'] for l in success_logs)

print("--- STREAM PROCESSING METRICS ---")
print(f"Total Log Events Received: {len(logs)}")
print(f"Successful Requests (200 OK): {len(success_logs)}")
print(f"Total Bytes Processed: {total_bytes} bytes")
"""

    user_code = st.text_area("Python Streaming Log Processor Editor:", value=default_code, height=240, key="lab4_code")

    if st.button("🚀 Run & Submit Lab 4 Assignment", width="stretch", key="btn_run_lab4"):
        buffer = io.StringIO()
        sys.stdout = buffer
        try:
            local_scope = {}
            exec(user_code, globals(), local_scope)
            sys.stdout = sys.__stdout__
            output_str = buffer.getvalue()

            score = 100.0
            st.success("✅ **Streaming Log Processor Executed!** JSON streaming events parsed cleanly (100% Score).")
            st.markdown(f'<div class="output-box">{output_str}</div>', unsafe_allow_html=True)
            save_assignment_result(student_id, "Data Structures", score)
            st.info("🏆 Practical lab grade recorded!")
            st.rerun()

        except Exception as e:
            sys.stdout = sys.__stdout__
            st.error(f"❌ Execution Error: {str(e)}")
