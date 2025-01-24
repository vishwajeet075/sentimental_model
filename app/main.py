import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.card import card
from streamlit_lottie import st_lottie
import requests

from datetime import datetime

from database import Database
from sentiment import SentimentAnalyzer
from utils import create_feedback_trend_chart, create_ratings_radar_chart, format_metrics

# Page config
st.set_page_config(
    page_title="Feedback Analysis System",
    page_icon="📊",
    layout="wide"
)

# Initialize database and sentiment analyzer
db = Database()
sentiment_analyzer = SentimentAnalyzer()

def load_lottie_url(url: str):
    r = requests.get(url)
    return r.json() if r.status_code == 200 else None

def show_admin_dashboard():
    st.sidebar.title("👨‍💻 Admin Dashboard")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.admin_logged_in = False
        st.experimental_rerun()

    # Get metrics
    metrics = db.get_feedback_metrics()
    if not metrics:
        st.warning("No feedback data available yet.")
        return

    formatted_metrics = format_metrics(metrics)
    
    # Header
    st.title("📊 Feedback Analytics Dashboard")
    
    # Metrics Overview
    col1, col2, col3 = st.columns(3)
    with col1:
        card("Total Feedback", f"📝 {formatted_metrics['total_feedback']}")
    with col2:
        card("Average Sentiment", f"😊 {formatted_metrics['avg_sentiment']}")
    with col3:
        card("Average Usability", f"⭐ {formatted_metrics['avg_usability']}/10")

    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Sentiment Trend
        feedback_trend = db.get_feedback_by_date()
        if feedback_trend:
            trend_chart = create_feedback_trend_chart(feedback_trend)
            st.plotly_chart(trend_chart, use_container_width=True)
    
    with col2:
        # Ratings Overview
        radar_chart = create_ratings_radar_chart(metrics)
        st.plotly_chart(radar_chart, use_container_width=True)

    # Recent Feedback
    st.subheader("📝 Recent Feedback")
    feedback_data = db.get_all_feedback()
    for feedback in feedback_data[-5:]:  # Show last 5 feedback entries
        with st.expander(f"Feedback from {feedback['created_at'].strftime('%Y-%m-%d %H:%M')}"):
            st.write(f"**Sentiment:** {feedback['sentiment_label']}")
            st.write(f"**Feedback:** {feedback['feedback_text']}")
            st.write(f"**Ratings:** Usability: {feedback['usability_rating']}/10, Performance: {feedback['performance_rating']}/10")

def show_user_feedback_form():
    col1, col2 = st.columns([2, 1])
    with col1:
        colored_header(
            label="🌟 Feature Feedback Portal",
            description="Help us improve your experience",
            color_name="blue-70"
        )
    with col2:
        lottie_feedback = load_lottie_url("https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json")
        st_lottie(lottie_feedback, height=200)

    with st.form("feedback_form"):
        # User Information
        col1, col2 = st.columns(2)
        with col1:
            user_role = st.selectbox(
                "What best describes your role?",
                ["Developer", "Designer", "Product Manager", "Business Analyst", "Other"]
            )
        with col2:
            experience_level = st.selectbox(
                "How long have you been using our platform?",
                ["Less than a month", "1-6 months", "6-12 months", "More than a year"]
            )

        # Feedback Text
        feedback_text = st.text_area(
            "Share your detailed feedback:",
            height=150
        )

        # Ratings
        col1, col2 = st.columns(2)
        with col1:
            usability_rating = st.slider("Usability Rating", 1, 10, 7)
            performance_rating = st.slider("Performance Rating", 1, 10, 7)
        with col2:
            ui_rating = st.slider("UI Rating", 1, 10, 7)
            documentation_rating = st.slider("Documentation Rating", 1, 10, 7)

        # Submit Button
        submitted = st.form_submit_button("Submit Feedback")
        
        if submitted:
            if not feedback_text.strip():
                st.error("Please provide feedback before submitting.")
                return

            # Analyze sentiment
            sentiment_result = sentiment_analyzer.analyze(feedback_text)
            
            # Prepare feedback data
            feedback_data = {
                "user_role": user_role,
                "experience_level": experience_level,
                "feedback_text": feedback_text,
                "usability_rating": usability_rating,
                "performance_rating": performance_rating,
                "ui_rating": ui_rating,
                "documentation_rating": documentation_rating,
                "sentiment_label": sentiment_result['label'],
                "sentiment_score": sentiment_result['score'],
                "sentiment_confidence": sentiment_result['confidence']
            }
            
            # Save to database
            db.save_feedback(feedback_data)
            
            # Show success message
            success_lottie = load_lottie_url("https://assets9.lottiefiles.com/packages/lf20_lk80fpsm.json")
            st_lottie(success_lottie, height=300, key="success")
            st.success("Thank you for your valuable feedback!")

def main():
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False

    # Admin login
    if not st.session_state.admin_logged_in:
        with st.sidebar:
            colored_header(
                label="Admin Login",
                description="Access dashboard",
                color_name="blue-70"
            )
            
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.button("Login", use_container_width=True):
                if db.verify_user(username, password):
                    st.session_state.admin_logged_in = True
                    st.experimental_rerun()
                else:
                    st.error("Invalid credentials.")

    # Show appropriate view
    if st.session_state.admin_logged_in:
        show_admin_dashboard()
    else:
        show_user_feedback_form()

if __name__ == "__main__":
    main()