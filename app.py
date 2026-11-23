"""
AI-Powered Personalized Learning Platform
Streamlit Entry Point Application with User Registration & Login.
"""

from html import escape

import streamlit as st

# Page Configuration - Must be the first Streamlit command
st.set_page_config(
    page_title="Learnwise | Student Learning",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.authentication import login_user, logout_user, is_logged_in, get_current_user, register_user
from database.database import init_db
from components.student_dashboard import render_student_dashboard
from components.recommendations import render_recommendations_page
from components.quiz import render_practice_quiz
from components.ai_tutor import render_ai_tutor
from components.my_performance import render_my_performance
from components.teacher_dashboard import render_teacher_dashboard
from components.analytics import render_analytics_page
from components.student_details import render_student_details_page
from components.practical_labs import render_practical_labs
from components.achievements import render_achievements_page

# Initialize Database & Run Migrations
init_db()

# Shared visual system for a consistent student and teacher experience.
st.markdown("""
<style>
    :root {
        --app-ink: #172033;
        --app-muted: #667085;
        --app-line: #e6eaf1;
        --app-surface: #ffffff;
        --app-canvas: #f5f7fb;
        --app-primary: #4f46e5;
        --app-primary-dark: #3730a3;
        --app-teal: #0f9f9a;
        --app-radius: 18px;
    }
    html, body, [class*="css"] { font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    html, body { background-color: var(--app-canvas) !important; color: var(--app-ink); }
    header { background-color: var(--app-canvas) !important; }
    .stApp, [data-testid="stAppViewContainer"] { background: var(--app-canvas); color: var(--app-ink); }
    header[data-testid="stHeader"], [data-testid="stHeader"] { background: var(--app-canvas) !important; box-shadow: none; }
    [data-testid="stToolbar"] { background: transparent; }
    .block-container { max-width: 1440px; padding-top: 2rem; padding-bottom: 4rem; }
    [data-testid="stSidebar"] { background: #fff; border-right: 1px solid var(--app-line); }
    [data-testid="stSidebar"] > div:first-child { padding-top: 1.25rem; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: var(--app-muted); }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        border-radius: 11px; padding: .5rem .65rem; transition: background .18s ease, color .18s ease;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background: #f2f3ff; color: var(--app-primary-dark); }
    .brand-lockup { display: flex; align-items: center; gap: 11px; margin: 0 0 1.2rem; }
    .brand-mark { display: grid; place-items: center; width: 42px; height: 42px; border-radius: 14px; color: #fff; background: linear-gradient(145deg, #6962f3, #3730a3); font-size: 21px; box-shadow: 0 8px 18px rgba(79,70,229,.24); }
    .brand-name { color: var(--app-ink); font-size: 15px; line-height: 1.2; font-weight: 800; }
    .brand-caption { display: block; color: #98a2b3; font-size: 11px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; margin-top: 4px; }
    .account-card { background: #f7f8fc; border: 1px solid var(--app-line); border-radius: 14px; padding: 13px; margin: .5rem 0 1rem; }
    .account-label { color: #98a2b3; font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: .1em; }
    .account-name { color: var(--app-ink); font-size: 14px; font-weight: 750; margin-top: 5px; overflow-wrap: anywhere; }
    .account-role { display: inline-block; color: var(--app-primary-dark); background: #e9e8ff; border-radius: 999px; padding: 3px 8px; margin-top: 8px; font-size: 10px; font-weight: 800; letter-spacing: .06em; }
    .sidebar-section-label { color: #98a2b3; font-size: 10px; font-weight: 800; letter-spacing: .12em; margin: .8rem 0 .4rem; }
    .page-header { margin: 0 0 1.45rem; padding: .15rem 0 1.05rem; border-bottom: 1px solid var(--app-line); }
    .page-eyebrow { display: flex; align-items: center; gap: 8px; color: var(--app-primary); font-size: 11px; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; margin-bottom: 8px; }
    .page-eyebrow-dot { width: 7px; height: 7px; background: var(--app-teal); border-radius: 50%; box-shadow: 0 0 0 4px #dbf5f1; }
    .page-title-row { display: flex; align-items: center; gap: 11px; }
    .page-title-row h1 { color: var(--app-ink); font-size: clamp(1.8rem, 3vw, 2.4rem); line-height: 1.15; font-weight: 800; letter-spacing: -.045em; margin: 0; }
    .page-icon { display: grid; place-items: center; flex: 0 0 42px; height: 42px; border-radius: 14px; background: #eeedff; font-size: 22px; }
    .page-header p { color: var(--app-muted); font-size: 14px; line-height: 1.65; margin: 9px 0 0; max-width: 780px; }
    h2, h3 { color: var(--app-ink); letter-spacing: -.025em; }
    [data-testid="stMetric"] { background: var(--app-surface); border: 1px solid var(--app-line); border-radius: 16px; padding: 17px 18px; box-shadow: 0 3px 12px rgba(16,24,40,.035); }
    [data-testid="stMetricLabel"] { color: var(--app-muted); font-size: 12px; font-weight: 650; white-space: normal; overflow-wrap: anywhere; }
    [data-testid="stMetricValue"] { color: var(--app-ink); font-size: clamp(1.05rem, 2vw, 1.55rem) !important; font-weight: 800; white-space: normal; overflow-wrap: anywhere; }
    [data-testid="stMetricDelta"] { font-size: 12px; }
    .stButton > button { min-height: 42px; border-radius: 11px; border: 1px solid #d8dcef; color: #3730a3; background: #fff; font-weight: 700; transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease; }
    .stButton > button:hover { border-color: #aaa6f5; color: #312e81; box-shadow: 0 5px 14px rgba(79,70,229,.12); transform: translateY(-1px); }
    .stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"] { border: 0; color: #fff; background: linear-gradient(135deg, #5b54ee, #4338ca); box-shadow: 0 7px 16px rgba(79,70,229,.2); }
    .stButton > button[kind="primary"]:hover, .stButton > button[data-testid="stBaseButton-primary"]:hover { color: #fff; background: linear-gradient(135deg, #4f46e5, #3730a3); }
    .stTextInput input, .stTextArea textarea, .stNumberInput input { border-radius: 10px; background: #fff; color: var(--app-ink) !important; border-color: #d5dae5; }
    .stTextInput input::placeholder, .stTextArea textarea::placeholder { color: #98a2b3 !important; opacity: 1; }
    .stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus { border-color: var(--app-primary); box-shadow: 0 0 0 2px rgba(79,70,229,.12); }
    [data-testid="stWidgetLabel"] p, [data-testid="stCaptionContainer"] p { color: var(--app-muted) !important; }
    [data-testid="stRadio"] label, [data-testid="stCheckbox"] label { color: var(--app-ink) !important; }
    [data-testid="stRadio"] label p, [data-testid="stCheckbox"] label p { color: var(--app-ink) !important; }
    input[type="radio"], input[type="checkbox"] { accent-color: var(--app-primary); }
    [data-testid="stTextInput"] button { color: var(--app-muted); background: #f7f8fc; }
    [data-baseweb="select"] > div { border-radius: 10px; }
    [data-testid="stProgressBar"] > div > div { background: linear-gradient(90deg, #5148e5, #0f9f9a); border-radius: 999px; }
    .stTabs [data-baseweb="tab-list"] { gap: 6px; background: #eceff5; border-radius: 13px; padding: 5px; }
    .stTabs [data-baseweb="tab"] { min-height: 39px; border-radius: 9px; color: #667085; font-weight: 700; }
    .stTabs [aria-selected="true"] { color: var(--app-primary-dark) !important; background: #fff; box-shadow: 0 2px 6px rgba(16,24,40,.08); }
    [data-testid="stDataFrame"], [data-testid="stTable"] { border: 1px solid var(--app-line); border-radius: 13px; overflow: hidden; }
    [data-testid="stAlert"] { border-radius: 13px; }
    [data-testid="stExpander"] { border: 1px solid var(--app-line); border-radius: 13px; background: #fff; }
    [data-testid="stVerticalBlockBorderWrapper"] { border-color: var(--app-line); border-radius: 16px; }
    .login-hero { padding: clamp(1.25rem, 4vw, 3.2rem) 0; }
    .login-kicker { display: inline-flex; align-items: center; gap: 8px; color: var(--app-primary); background: #eeedff; border-radius: 999px; padding: 7px 11px; font-size: 10px; font-weight: 850; letter-spacing: .13em; }
    .login-hero h1 { color: var(--app-ink); font-size: clamp(2.6rem, 5.5vw, 4.5rem); font-weight: 850; line-height: 1.04; letter-spacing: -.065em; margin: 1.2rem 0 1rem; }
    .login-hero h1 span { color: var(--app-primary); }
    .login-hero-copy { max-width: 540px; color: var(--app-muted); font-size: 16px; line-height: 1.75; }
    .login-feature-list { display: grid; gap: 13px; margin-top: 1.8rem; }
    .login-feature { display: flex; align-items: flex-start; gap: 11px; color: var(--app-ink); font-size: 13px; line-height: 1.5; }
    .login-feature-mark { display: grid; place-items: center; flex: 0 0 27px; height: 27px; border-radius: 9px; background: #e8f8f5; color: #07857f; font-weight: 900; }
    .auth-panel { padding: 1rem 0; }
    .auth-panel-title { color: var(--app-ink); font-size: 22px; font-weight: 800; letter-spacing: -.035em; margin: 0 0 4px; }
    .auth-panel-copy { color: var(--app-muted); font-size: 13px; margin: 0 0 1.1rem; }
    .demo-credentials { background: #f7f8fc; border: 1px dashed #cdd2e0; padding: 13px 15px; border-radius: 12px; font-size: 12px; line-height: 1.75; margin-top: 1rem; color: #4b5565; }
    .demo-credentials code { color: #3730a3; background: #eeedff; border-radius: 5px; padding: 2px 5px; }
    @media (max-width: 900px) {
        .block-container { padding: 1.1rem 1rem 2.5rem; }
        .page-header { margin-bottom: 1rem; }
        .page-title-row h1 { font-size: 1.75rem; }
        .page-icon { flex-basis: 36px; height: 36px; font-size: 18px; }
        [data-testid="stHorizontalBlock"] { display: grid !important; grid-template-columns: repeat(2, minmax(0, 1fr)) !important; gap: .75rem; }
        [data-testid="stHorizontalBlock"] > div { width: auto !important; min-width: 0 !important; flex: initial !important; }
    }
    @media (max-width: 520px) {
        [data-testid="stHorizontalBlock"] { grid-template-columns: minmax(0, 1fr) !important; }
    }
</style>
""", unsafe_allow_html=True)

def render_login():
    """Render the responsive sign-in and registration landing screen."""
    col_intro, col_auth = st.columns([1.1, 1])
    with col_intro:
        st.markdown("""
            <section class="login-hero">
                <div class="login-kicker">✦ AI-POWERED STUDENT SUCCESS</div>
                <h1>Learn at your pace.<br><span>Grow with purpose.</span></h1>
                <p class="login-hero-copy">A learning space that adapts to your progress. Find the right resources, practise with confidence, and see how far you have come.</p>
                <div class="login-feature-list">
                    <div class="login-feature"><span class="login-feature-mark">✓</span><span><strong>A path made for you</strong><br>Recommendations shaped by your strengths and focus areas.</span></div>
                    <div class="login-feature"><span class="login-feature-mark">✓</span><span><strong>Learn by doing</strong><br>Course quizzes, practical labs, and an always-ready academic tutor.</span></div>
                    <div class="login-feature"><span class="login-feature-mark">✓</span><span><strong>Progress you can see</strong><br>Track your performance, learning streaks, and achievements.</span></div>
                </div>
            </section>
        """, unsafe_allow_html=True)

    with col_auth:
        st.markdown("""
            <div class="auth-panel">
                <div class="auth-panel-title">Welcome to your learning space</div>
                <p class="auth-panel-copy">Sign in or create an account to continue.</p>
            </div>
        """, unsafe_allow_html=True)
        tab_login, tab_signup = st.tabs(["Sign in", "Create account"])

        with tab_login:
            role = st.radio("Select Role", ["Student", "Teacher"], horizontal=True, key="login_role_radio")
            username = st.text_input("Username", placeholder="Enter your username", key="login_user_input")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass_input")

            if st.button("Sign in →", type="primary", width="stretch", key="btn_login_submit"):
                user = login_user(username, password)
                if user and user["role"].lower() == role.lower():
                    st.session_state["user"] = user
                    st.success(f"Welcome back, {user['name']}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials or role mismatch. Please check details.")

            st.markdown("""
                <div class="demo-credentials">
                    <strong>Demo accounts</strong><br>
                    Student: <code>student1</code> / <code>student123</code><br>
                    Teacher: <code>teacher1</code> / <code>teacher123</code>
                </div>
            """, unsafe_allow_html=True)

        with tab_signup:
            reg_role = st.radio("Account Type", ["Student", "Teacher"], horizontal=True, key="signup_role_radio")
            reg_name = st.text_input("Full Name", placeholder="e.g. Ananya Rao", key="signup_name_input")
            reg_user = st.text_input("Choose Username", placeholder="e.g. ananya1", key="signup_user_input")
            reg_pass = st.text_input("Choose Password", type="password", placeholder="At least 4 characters", key="signup_pass_input")
            reg_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", key="signup_confirm_input")

            if st.button("Create account →", type="primary", width="stretch", key="btn_signup_submit"):
                if reg_pass != reg_confirm:
                    st.error("Passwords do not match. Please re-enter passwords.")
                else:
                    success, msg = register_user(reg_name, reg_user, reg_pass, reg_role)
                    if success:
                        st.success(msg)
                        st.info("You can now switch to the 'Sign In' tab and log in with your new credentials!")
                    else:
                        st.error(msg)

def main():
    if not is_logged_in():
        render_login()
        return

    current_user = get_current_user()
    role_str = str(current_user.get("role", "")).lower()

    safe_name = escape(str(current_user.get("name", "Student")))
    safe_role = escape(role_str.upper())
    st.sidebar.markdown("""
        <div class="brand-lockup">
            <div class="brand-mark">✦</div>
            <div><div class="brand-name">Learnwise</div><span class="brand-caption">Personal learning</span></div>
        </div>
    """, unsafe_allow_html=True)
    st.sidebar.markdown(f"""
        <div class="account-card">
            <div class="account-label">Signed in as</div>
            <div class="account-name">{safe_name}</div>
            <span class="account-role">{safe_role}</span>
        </div>
        <div class="sidebar-section-label">YOUR WORKSPACE</div>
    """, unsafe_allow_html=True)

    if role_str == "student":
        student_id = current_user.get("student_id", 1)

        nav_options = [
            "📊 Dashboard & Overview",
            "📚 Learning Resources & Catalogue",
            "📝 Practice Quiz (Course-Wise)",
            "🧪 Practical DE & AI Coding Labs",
            "🤖 AI Academic Tutor",
            "📈 My Performance & Weaknesses",
            "🏆 Goals & Achievements"
        ]
        
        # Handle pending navigation before widget instantiation
        if 'pending_nav' in st.session_state:
            target = st.session_state.pop('pending_nav')
            if target in nav_options:
                st.session_state['student_nav_radio_main'] = target
                st.session_state['active_learning_resource'] = None

        if 'student_nav_radio_main' not in st.session_state:
            if st.session_state.get('active_learning_resource'):
                st.session_state['student_nav_radio_main'] = "📚 Learning Resources & Catalogue"
            else:
                st.session_state['student_nav_radio_main'] = "📊 Dashboard & Overview"

        if st.session_state.get("quiz_active", False):
            st.sidebar.warning("🔒 EXAM LOCKOUT ACTIVE")
            st.sidebar.info("Navigation is locked during the timed exam. You can switch modules after submitting or canceling it.")
            selected_nav = "📝 Practice Quiz (Course-Wise)"
        else:
            selected_nav = st.sidebar.radio(
                "Student modules",
                nav_options,
                key="student_nav_radio_main"
            )

        # Clear active resource if user navigates away from Learning Resources
        if selected_nav != "📚 Learning Resources & Catalogue":
            st.session_state['active_learning_resource'] = None

        if selected_nav == "📊 Dashboard & Overview":
            render_student_dashboard(student_id)
        elif selected_nav == "📚 Learning Resources & Catalogue":
            render_recommendations_page(student_id)
        elif selected_nav == "📝 Practice Quiz (Course-Wise)":
            render_practice_quiz(student_id)
        elif selected_nav == "🧪 Practical DE & AI Coding Labs":
            render_practical_labs(student_id)
        elif selected_nav == "🤖 AI Academic Tutor":
            render_ai_tutor(student_id)
        elif selected_nav == "📈 My Performance & Weaknesses":
            render_my_performance(student_id)
        elif selected_nav == "🏆 Goals & Achievements":
            render_achievements_page(student_id)

    elif role_str == "teacher":
        selected_nav = st.sidebar.radio(
            "Teacher workspace",
            [
                "🏫 Class Overview & Analytics",
                "📈 ML Classifier & Topic Stats",
                "🔍 Inspect Student Details"
            ],
            key="teacher_nav_radio_main"
        )

        if selected_nav == "🏫 Class Overview & Analytics":
            render_teacher_dashboard()
        elif selected_nav == "📈 ML Classifier & Topic Stats":
            render_analytics_page()
        elif selected_nav == "🔍 Inspect Student Details":
            render_student_details_page()

    st.sidebar.markdown("---")
    if st.sidebar.button("Logout 🚪", key="btn_logout", width="stretch"):
        st.session_state.pop('active_learning_resource', None)
        logout_user()
        st.rerun()

if __name__ == "__main__":
    main()
