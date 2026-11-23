"""
Class Analytics and ML Model Performance Component.
Displays deep-dive topic analytics and machine learning classification evaluation.
"""

import streamlit as st
import plotly.express as px
import pandas as pd
from utils.helpers import calculate_class_statistics, identify_difficult_topics
from ml.train_model import train_model
from components.ui import render_page_header

def render_class_analytics():
    """Render full Class Analytics and ML Evaluation page."""
    render_page_header(
        "TEACHER WORKSPACE",
        "Class analytics & model insights",
        "Explore curriculum difficulty, student outcomes, and the signals behind learning-level predictions.",
        "📊",
    )

    tab1, tab2 = st.tabs(["📚 Curriculum & Topic Analytics", "🤖 Machine Learning Model Metrics"])

    with tab1:
        st.subheader("📌 Topic Difficulty Analysis")
        diff_topics = identify_difficult_topics()
        if diff_topics:
            df_diff = pd.DataFrame(diff_topics)
            st.dataframe(
                df_diff[['subject', 'topic', 'avg_score', 'struggling_count', 'total_students', 'struggle_pct', 'status']],
                width="stretch"
            )
            
            fig_diff = px.bar(
                df_diff,
                x='topic',
                y='struggle_pct',
                color='subject',
                title="Class Struggle Percentage by Topic (%)",
                labels={'topic': 'Topic', 'struggle_pct': 'Struggling Students (%)'}
            )
            fig_diff.update_layout(yaxis_range=[0, 100], height=380)
            st.plotly_chart(fig_diff, width="stretch")
        else:
            st.info("No high-difficulty topics detected.")

    with tab2:
        st.subheader("🤖 Random Forest Classifier Evaluation")
        st.caption("Model trained on student performance metrics to predict learning levels (Beginner, Intermediate, Advanced).")

        col_train, col_space = st.columns([1, 2])
        with col_train:
            if st.button("🔄 Retrain ML Model Live", width="stretch"):
                with st.spinner("Retraining Random Forest model..."):
                    eval_results = train_model()
                    st.success(f"Model retrained! New Accuracy: {eval_results['accuracy']}%")
                    st.session_state['ml_eval'] = eval_results

        eval_data = st.session_state.get('ml_eval')
        if not eval_data:
            eval_data = train_model()
            st.session_state['ml_eval'] = eval_data

        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Model Accuracy", f"{eval_data['accuracy']}%")
        with m2:
            st.metric("Classifier Type", "Random Forest")
        with m3:
            st.metric("Trees Count", "100 Estimators")

        st.markdown("---")
        st.subheader("📊 Feature Importance Breakdown")
        st.caption("Shows which student features contribute most to learning level prediction.")

        feat_imp = eval_data['feature_importances']
        df_feat = pd.DataFrame({
            'Feature': list(feat_imp.keys()),
            'Importance': list(feat_imp.values())
        }).sort_values(by='Importance', ascending=True)

        fig_feat = px.bar(
            df_feat,
            x='Importance',
            y='Feature',
            orientation='h',
            title="Random Forest Feature Importances",
            color='Importance',
            color_continuous_scale='Blues'
        )
        fig_feat.update_layout(height=350)
        st.plotly_chart(fig_feat, width="stretch")

# Function alias to support both import conventions
render_analytics_page = render_class_analytics
