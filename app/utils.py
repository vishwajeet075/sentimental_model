import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

def create_feedback_trend_chart(feedback_data):
    """Create feedback trend chart"""
    df = pd.DataFrame(feedback_data)
    fig = px.line(df, x="_id", y="avg_sentiment", 
                  title="Feedback Sentiment Trend",
                  labels={"_id": "Date", "avg_sentiment": "Average Sentiment"})
    fig.update_traces(mode="lines+markers")
    return fig

def create_ratings_radar_chart(metrics):
    """Create radar chart for different ratings"""
    categories = ['Usability', 'Performance', 'UI', 'Documentation']
    values = [
        metrics['avg_usability'],
        metrics['avg_performance'],
        metrics['avg_ui'],
        metrics['avg_documentation']
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Average Ratings'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )),
        showlegend=False,
        title="Rating Metrics Overview"
    )
    return fig

def format_metrics(metrics):
    """Format metrics for display"""
    return {
        'total_feedback': metrics['total_feedback'],
        'avg_sentiment': round(metrics['avg_sentiment'], 2),
        'avg_usability': round(metrics['avg_usability'], 2),
        'avg_performance': round(metrics['avg_performance'], 2),
        'avg_ui': round(metrics['avg_ui'], 2),
        'avg_documentation': round(metrics['avg_documentation'], 2)
    }