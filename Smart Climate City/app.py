"""
Project EcoFlow - Smart Traffic Control Dashboard
Premium Streamlit interface for demonstrating intelligent traffic management
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from logic import SmartIntersection, calculate_health_impact
from model import TrafficPredictor
from config import HEILBRONN_COORDS, MODEL_PATH, TRAINING_DATA_MONTHS
import psycopg2

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="EcoFlow - Smart Traffic Control",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS FOR PREMIUM DESIGN
# ============================================================================
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }

    /* Main container - Clean light background */
    .main {
        background: #f5f7fa;
        padding: 2rem;
    }

    .block-container {
        background: #ffffff;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    /* Title styling - Dark, high contrast */
    h1 {
        color: #1a1a1a;
        font-weight: 700;
        text-align: center;
        font-size: 3rem;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }

    /* Subtitle - Dark gray for better readability */
    .subtitle {
        text-align: center;
        color: #4a5568;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        font-weight: 500;
    }

    /* Headings - Dark for readability */
    h2, h3, h4, h5, h6 {
        color: #1a1a1a;
        font-weight: 600;
    }

    /* Body text - Dark for readability */
    p, div, span {
        color: #2d3748;
    }

    /* Metric cards - Clean white background with subtle border */
    [data-testid="stMetric"] {
        background: #ffffff;
        border-radius: 8px;
        padding: 1rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    /* Metric labels - Dark for readability */
    [data-testid="stMetric"] label {
        color: #4a5568 !important;
        font-weight: 500;
    }

    /* Metric values - Dark for readability */
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #1a1a1a !important;
    }

    /* Sidebar - Clean dark background with good contrast */
    [data-testid="stSidebar"] {
        background: #1e293b;
    }

    [data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }

    [data-testid="stSidebar"] label {
        color: #cbd5e1 !important;
        font-weight: 500;
    }

    /* Sidebar headings */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }

    /* Time input - White text for better readability (both when typing and when displaying selected value) */
    div[data-testid="stTimeInput"] input,
    div[data-testid="stTimeInput"] input::placeholder,
    div[data-testid="stTimeInput"] input[value],
    div[data-testid="stTimeInput"] [data-baseweb="input"] input,
    div[data-testid="stTimeInput"] [data-baseweb="input"] input::placeholder,
    div[data-testid="stTimeInput"] [data-baseweb="input"] input[type="text"],
    div[data-testid="stTimeInput"] [data-baseweb="input"] input[type="time"],
    div[data-testid="stTimeInput"] [data-baseweb="input"] input[value],
    div[data-testid="stTimeInput"] [data-baseweb="input"] > div > input,
    div[data-testid="stTimeInput"] [data-baseweb="input"] > div > input[value] {
        color: #ffffff !important;
        background-color: #1e293b !important;
    }

    /* Ensure the displayed value in time input is white */
    div[data-testid="stTimeInput"] [data-baseweb="input"] input::-webkit-input-placeholder,
    div[data-testid="stTimeInput"] [data-baseweb="input"] input::-moz-placeholder,
    div[data-testid="stTimeInput"] [data-baseweb="input"] input:-ms-input-placeholder {
        color: #ffffff !important;
        opacity: 0.8;
    }

    div[data-testid="stTimeInput"] label {
        color: #ffffff !important;
    }

    /* Date input - White text for better readability */
    div[data-testid="stDateInput"] input,
    div[data-testid="stDateInput"] input[type="text"],
    div[data-testid="stDateInput"] input[type="date"] {
        color: #ffffff !important;
        background-color: #1e293b !important;
    }

    div[data-testid="stDateInput"] label {
        color: #ffffff !important;
    }

    /* Number input - White text for better readability */
    div[data-testid="stNumberInput"] input {
        color: #ffffff !important;
        background-color: #1e293b !important;
    }

    /* BaseWeb input styling for time picker - more specific */
    [data-baseweb="input"] input,
    [data-baseweb="input"] input[type="text"],
    [data-baseweb="input"] input[type="time"],
    [data-baseweb="input"] input[value],
    [data-baseweb="input"] > div > input,
    [data-baseweb="input"] > div > input[value] {
        color: #ffffff !important;
    }

    [data-baseweb="input"] input::placeholder,
    [data-baseweb="input"] input::-webkit-input-placeholder,
    [data-baseweb="input"] input::-moz-placeholder,
    [data-baseweb="input"] input:-ms-input-placeholder {
        color: #ffffff !important;
        opacity: 0.8;
    }

    /* Time picker dropdown/select elements */
    [data-baseweb="select"] {
        color: #ffffff !important;
    }

    [data-baseweb="select"] input,
    [data-baseweb="select"] input[value] {
        color: #ffffff !important;
    }

    /* Force white color for all text in time input container */
    div[data-testid="stTimeInput"] * {
        color: #ffffff !important;
    }

    /* Exception: keep labels and help text readable but ensure input values are white */
    div[data-testid="stTimeInput"] [data-baseweb="input"] {
        color: #ffffff !important;
    }

    div[data-testid="stTimeInput"] [data-baseweb="input"] * {
        color: #ffffff !important;
    }

    /* Buttons - Primary blue with good contrast */
    .stButton>button {
        background: #2563eb;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.3);
        transition: all 0.2s ease;
    }

    .stButton>button:hover {
        background: #1d4ed8;
        box-shadow: 0 4px 8px rgba(37, 99, 235, 0.4);
    }

    /* Status boxes - Improved contrast */
    .status-box {
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }

    .status-box:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* Info boxes - Better contrast */
    .stAlert {
        border-radius: 8px;
    }

    /* Radio buttons and sliders - Better visibility */
    [data-testid="stRadio"] label {
        color: #f1f5f9 !important;
    }

    [data-testid="stSlider"] label {
        color: #f1f5f9 !important;
    }

    [data-testid="stNumberInput"] label {
        color: #f1f5f9 !important;
    }

    /* Captions - Dark gray for readability */
    [data-testid="stCaption"] {
        color: #4a5568 !important;
    }

    /* Markdown text - Dark for readability */
    .stMarkdown {
        color: #2d3748;
    }

    /* Traffic light animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }

    .traffic-light {
        animation: pulse 2s ease-in-out infinite;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER
# ============================================================================
st.markdown("# 🚦 EcoFlow")
st.markdown('<p class="subtitle">Intelligent Traffic Control for Cleaner Cities</p>', unsafe_allow_html=True)

# ============================================================================
# AI PREDICTION DISPLAY
# ============================================================================
@st.cache_resource(show_spinner=False)
def load_traffic_model(_model_version=None):
    """
    Load the trained Prophet model.
    _model_version parameter is used to bust cache when model is retrained.
    """
    predictor = TrafficPredictor()
    if predictor.load_model(MODEL_PATH):
        return predictor
    return None

@st.cache_data(ttl=3600)  # Cache for 1 hour (stats don't change often)
def get_traffic_statistics():
    """
    Analyze historical traffic data to extract statistics like rush hour times,
    average traffic by hour, peak times, etc.
    """
    try:
        data_path = f'data_cache/german_traffic_{TRAINING_DATA_MONTHS}m.csv'
        if not os.path.exists(data_path):
            return None

        df = pd.read_csv(data_path)
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.day_name()
        df['is_weekend'] = df['day_of_week'].isin(['Saturday', 'Sunday'])

        # Aggregate to hourly averages
        hourly_stats = df.groupby('hour')['total_traffic'].agg(['mean', 'median', 'max']).reset_index()
        hourly_stats['vehicles_per_hour'] = (hourly_stats['mean'] * 60).round(0).astype(int)

        # Find rush hours (hours with traffic > 75th percentile)
        traffic_75th = hourly_stats['mean'].quantile(0.75)
        rush_hours = hourly_stats[hourly_stats['mean'] >= traffic_75th]['hour'].tolist()

        # Find peak hour
        peak_hour = hourly_stats.loc[hourly_stats['mean'].idxmax(), 'hour']
        peak_traffic = int(hourly_stats.loc[hourly_stats['mean'].idxmax(), 'vehicles_per_hour'])

        # Find quiet hours (hours with traffic < 25th percentile)
        traffic_25th = hourly_stats['mean'].quantile(0.25)
        quiet_hours = hourly_stats[hourly_stats['mean'] <= traffic_25th]['hour'].tolist()

        # Average traffic overall
        avg_traffic = int(df['total_traffic'].mean() * 60)

        # Weekday vs Weekend comparison
        weekday_avg = int(df[~df['is_weekend']]['total_traffic'].mean() * 60)
        weekend_avg = int(df[df['is_weekend']]['total_traffic'].mean() * 60)

        # Format rush hour times
        def format_hours(hour_list):
            if not hour_list:
                return "None"
            hour_list = sorted(hour_list)
            # Group consecutive hours
            ranges = []
            start = hour_list[0]
            end = hour_list[0]

            for i in range(1, len(hour_list)):
                if hour_list[i] == end + 1:
                    # Consecutive, extend range
                    end = hour_list[i]
                else:
                    # Break in sequence, save current range
                    if start == end:
                        ranges.append(f"{start:02d}:00")
                    else:
                        ranges.append(f"{start:02d}:00-{end:02d}:00")
                    start = hour_list[i]
                    end = hour_list[i]

            # Add final range
            if start == end:
                ranges.append(f"{start:02d}:00")
            else:
                ranges.append(f"{start:02d}:00-{end:02d}:00")

            return ", ".join(ranges)

        return {
            'avg_traffic': avg_traffic,
            'peak_hour': peak_hour,
            'peak_traffic': peak_traffic,
            'rush_hours': rush_hours,
            'rush_hours_formatted': format_hours(rush_hours),
            'quiet_hours': quiet_hours,
            'quiet_hours_formatted': format_hours(quiet_hours),
            'hourly_stats': hourly_stats,
            'weekday_avg': weekday_avg,
            'weekend_avg': weekend_avg
        }
    except Exception as e:
        print(f"Error calculating statistics: {e}")
        return None

@st.cache_data(ttl=900)  # Cache for 15 minutes (900 seconds) for faster updates
def get_cached_predictions(current_15min_key, minutes_ahead, model_version=None):
    """
    Get cached predictions (refreshes every 15 minutes).
    current_15min_key ensures cache refreshes every 15 minutes.
    minutes_ahead: How many minutes ahead to predict (used as part of cache key).
    model_version helps bust cache when model is retrained.
    """
    # Use model file modification time as version to bust cache on retrain
    import os
    model_version = os.path.getmtime(MODEL_PATH) if os.path.exists(MODEL_PATH) else 0
    predictor = load_traffic_model(_model_version=model_version)
    if predictor:
        # Always try to include directions if available
        return predictor.get_current_prediction(include_directions=True, minutes_ahead=minutes_ahead)
    return None

# ============================================================================
# PREDICTION TIME SELECTOR
# ============================================================================
# Initialize default prediction time (15 minutes ahead)
prediction_minutes_ahead = 15
selected_datetime = None

if os.path.exists(MODEL_PATH):
    st.markdown("### ⏰ Select Prediction Time")

    now = datetime.now()

    # Create columns for date and time selection
    col_date, col_time, col_info = st.columns([1.5, 1, 1.5])

    with col_date:
        # Date selector - default to today, allow up to end of 2026
        # Calculate max date as December 31, 2026
        max_date = datetime(2026, 12, 31).date()
        if max_date < now.date():
            # If we're already past 2026, allow 2 years ahead
            max_date = now.date() + timedelta(days=730)

        selected_date = st.date_input(
            "Date",
            value=now.date(),
            min_value=now.date(),
            max_value=max_date,
            help="Select the date for prediction (up to end of 2026 or 2 years ahead)"
        )

    with col_time:
        # Time selector - default to 15 minutes from now, rounded to nearest 15 minutes
        default_time = (now + timedelta(minutes=15)).replace(second=0, microsecond=0)
        # Round to nearest 15 minutes
        default_minute = (default_time.minute // 15) * 15
        default_time = default_time.replace(minute=default_minute)

        selected_time = st.time_input(
            "Time",
            value=default_time.time(),
            help="Select the time for prediction (in 15-minute increments)"
        )

    with col_info:
        # Combine date and time
        selected_datetime = datetime.combine(selected_date, selected_time)

        # If selected time is in the past (same day but earlier time), use tomorrow instead
        if selected_date == now.date() and selected_datetime < now:
            selected_datetime = selected_datetime + timedelta(days=1)
            date_display = "Tomorrow"
        elif selected_date == now.date():
            date_display = "Today"
        elif selected_date == now.date() + timedelta(days=1):
            date_display = "Tomorrow"
        else:
            date_display = selected_date.strftime("%B %d")

        # Calculate minutes from now to selected time
        time_diff = selected_datetime - now
        prediction_minutes_ahead = int(time_diff.total_seconds() / 60)

        # Format display
        current_time_str = now.strftime("%H:%M")
        target_time_str = selected_datetime.strftime("%H:%M")

        # Show info box
        days_ahead = prediction_minutes_ahead // (24 * 60)
        if prediction_minutes_ahead < 0:
            st.error(f"⚠️ Selected time is in the past!\nPlease choose a future time.")
        elif prediction_minutes_ahead > 365 * 24 * 60:  # More than 1 year
            st.warning(f"⚠️ Long-term prediction ({days_ahead} days ahead). Accuracy may decrease significantly over time.")
        elif prediction_minutes_ahead > 30 * 24 * 60:  # More than 30 days
            st.info(f"ℹ️ Medium-term prediction ({days_ahead} days ahead). Predictions are based on historical patterns.")
        else:
            hours_ahead = prediction_minutes_ahead // 60
            mins_ahead = prediction_minutes_ahead % 60
            if hours_ahead > 0:
                time_ahead_str = f"{hours_ahead}h {mins_ahead}m"
            else:
                time_ahead_str = f"{mins_ahead}m"

            st.markdown(f"""
            <div style="background: #1e293b; padding: 1rem; border-radius: 8px; margin-top: 1.5rem;">
                <p style="margin: 0; color: #ffffff; font-size: 0.9rem;"><strong>Current:</strong> {current_time_str}</p>
                <p style="margin: 0.25rem 0 0 0; color: #ffffff; font-size: 0.9rem;"><strong>Predicting:</strong> {date_display} {target_time_str}</p>
                <p style="margin: 0.25rem 0 0 0; color: #ffffff; font-size: 0.85rem;">({time_ahead_str} ahead)</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

# Display AI predictions if model exists
if os.path.exists(MODEL_PATH):
    try:
        # Show loading indicator while fetching predictions
        # Use current 15-minute window as cache key to refresh predictions every 15 minutes
        now = datetime.now()
        current_15min_key = now.replace(second=0, microsecond=0, minute=(now.minute // 15) * 15)
        # Use model file modification time to bust cache when model is retrained
        import os
        model_version = os.path.getmtime(MODEL_PATH) if os.path.exists(MODEL_PATH) else 0

        # Only make predictions if the selected time is in the future
        if prediction_minutes_ahead >= 0:
            with st.spinner("🤖 Loading AI predictions..."):
                current_pred = get_cached_predictions(current_15min_key, prediction_minutes_ahead, model_version=model_version)
        else:
            current_pred = None
            st.warning("⚠️ Please select a future time for prediction.")

        if current_pred:
            st.markdown("---")
            st.markdown("### 🤖 Real-Time AI Predictions")

            # Check if we have direction data (TR1 and TR2)
            has_directions = 'direction_1' in current_pred and 'direction_2' in current_pred

            if has_directions:
                st.markdown('<p style="color: #4a5568; font-size: 0.95rem; margin-bottom: 1.5rem;">Based on Prophet ML models trained on 18,701 15-minute intervals (aggregated from 222,402 measurements, 12 months) from Fulda, Germany<br><small>✅ Separate models for Direction 1 (TR1) and Direction 2 (TR2) | Predictions in vehicles per minute</small></p>', unsafe_allow_html=True)
            else:
                st.markdown('<p style="color: #4a5568; font-size: 0.95rem; margin-bottom: 1.5rem;">Based on Prophet ML model trained on 18,701 15-minute intervals (aggregated from 222,402 measurements, 12 months) from Fulda, Germany<br><small>Note: Predictions are in vehicles per minute (typical range: 3-15, rush hour: 20-30)</small></p>', unsafe_allow_html=True)

            if has_directions:
                # Show direction-specific predictions with more space
                col_ai1, col_ai2, col_ai3 = st.columns(3)
            else:
                col_ai1, col_ai2, col_ai3 = st.columns(3)

            with col_ai1:
                # Data is in vehicles per minute, convert to hourly for display
                # Training data: average 12.3 vehicles/min, max 136 vehicles/min
                vehicles_per_min = current_pred['predicted_traffic']
                hourly_traffic = int(vehicles_per_min * 60)
                lower_bound_hr = int(current_pred['lower_bound'] * 60)
                upper_bound_hr = int(current_pred['upper_bound'] * 60)

                help_text = f"Prediction: {vehicles_per_min:.1f} vehicles/min = {hourly_traffic} vehicles/hour. Based on Prophet model (avg: 12.3/min, max observed: 136/min)"

                st.metric(
                    label="AI Predicted Traffic (Now)",
                    value=f"{hourly_traffic} cars/hr",
                    delta=f"{vehicles_per_min:.1f} vehicles/min | Range: {lower_bound_hr}-{upper_bound_hr}",
                    help=help_text
                )

            with col_ai2:
                # Determine status based on predicted traffic
                # Based on real data analysis:
                # - Low: < 500 vehicles/hour (< 8.3 vehicles/min) - below average
                # - Normal: 500-1500 vehicles/hour (8.3-25 vehicles/min) - typical range
                # - High: > 1500 vehicles/hour (> 25 vehicles/min) - rush hour levels
                if hourly_traffic < 500:
                    status_icon = "🟢"
                    status_text = "Low Traffic Expected"
                    delta_color = "normal"
                elif hourly_traffic > 1500:
                    status_icon = "⚡"
                    status_text = "High Traffic Expected"
                    delta_color = "inverse"
                else:
                    status_icon = "✅"
                    status_text = "Normal Traffic Expected"
                    delta_color = "normal"

                confidence_range = int((current_pred['upper_bound'] - current_pred['lower_bound']) * 30)
                st.metric(
                    label="AI Forecast Status",
                    value=f"{status_icon} {status_text}",
                    delta=f"Confidence: ±{confidence_range} cars/hr",
                    delta_color=delta_color,
                    help=f"Prediction range: {lower_bound_hr} - {upper_bound_hr} cars/hr"
                )

            with col_ai3:
                pred_time = current_pred['timestamp']
                if isinstance(pred_time, pd.Timestamp):
                    time_str = pred_time.strftime('%H:%M')
                    # Show current time for comparison
                    current_time = datetime.now().strftime('%H:%M')
                else:
                    time_str = pred_time.strftime('%H:%M') if hasattr(pred_time, 'strftime') else str(pred_time)[:5]
                    current_time = datetime.now().strftime('%H:%M')

                # Show prediction timeframe
                pred_minutes_ahead = current_pred.get('target_minutes_ahead', 15)
                pred_hours = pred_minutes_ahead // 60
                pred_mins = pred_minutes_ahead % 60
                if pred_hours > 0:
                    time_ahead_str = f"{pred_hours}h {pred_mins}m"
                else:
                    time_ahead_str = f"{pred_mins}m"

                # Show selected date/time if available
                if selected_datetime:
                    selected_date_str = selected_datetime.strftime("%Y-%m-%d %H:%M")
                    if selected_datetime.date() == datetime.now().date():
                        date_label = "Today"
                    elif selected_datetime.date() == (datetime.now() + timedelta(days=1)).date():
                        date_label = "Tomorrow"
                    else:
                        date_label = selected_datetime.strftime("%b %d")
                    time_display = f"{date_label} {selected_datetime.strftime('%H:%M')}"
                else:
                    time_display = time_str

                st.metric(
                    label="Prediction Time",
                    value=f"{time_display}",
                    delta=f"{time_ahead_str} ahead | Current: {current_time}",
                    help=f"Prediction for {time_display} ({time_ahead_str} ahead) | Current time: {current_time}"
                )

            # Show direction-specific predictions if available
            if has_directions:
                st.markdown("---")
                st.markdown("### 📍 Direction-Specific Predictions")

                tr1_per_min = current_pred['direction_1']
                tr2_per_min = current_pred['direction_2']
                tr1_hr = int(tr1_per_min * 60)
                tr2_hr = int(tr2_per_min * 60)
                tr1_lower_hr = int(current_pred.get('direction_1_lower', tr1_per_min * 0.8) * 60)
                tr1_upper_hr = int(current_pred.get('direction_1_upper', tr1_per_min * 1.2) * 60)
                tr2_lower_hr = int(current_pred.get('direction_2_lower', tr2_per_min * 0.8) * 60)
                tr2_upper_hr = int(current_pred.get('direction_2_upper', tr2_per_min * 1.2) * 60)

                # Calculate direction split
                total_dir = tr1_per_min + tr2_per_min
                if total_dir > 0:
                    tr1_pct = int((tr1_per_min / total_dir) * 100)
                    tr2_pct = int((tr2_per_min / total_dir) * 100)
                else:
                    tr1_pct = tr2_pct = 50

                col_dir1, col_dir2, col_dir3 = st.columns(3)

                with col_dir1:
                    st.metric(
                        label="🔄 Direction 1 (TR1)",
                        value=f"{tr1_hr} cars/hr",
                        delta=f"{tr1_per_min:.1f} vehicles/min ({tr1_pct}%)",
                        help=f"Direction 1 prediction: {tr1_per_min:.1f} vehicles/min = {tr1_hr} vehicles/hour\nRange: {tr1_lower_hr}-{tr1_upper_hr} vehicles/hr"
                    )

                with col_dir2:
                    st.metric(
                        label="🔄 Direction 2 (TR2)",
                        value=f"{tr2_hr} cars/hr",
                        delta=f"{tr2_per_min:.1f} vehicles/min ({tr2_pct}%)",
                        help=f"Direction 2 prediction: {tr2_per_min:.1f} vehicles/min = {tr2_hr} vehicles/hour\nRange: {tr2_lower_hr}-{tr2_upper_hr} vehicles/hr"
                    )

                with col_dir3:
                    # Calculate direction balance
                    direction_ratio = max(tr1_per_min, tr2_per_min) / min(tr1_per_min, tr2_per_min) if min(tr1_per_min, tr2_per_min) > 0 else 1
                    if direction_ratio > 2:
                        balance_status = f"⚠️ Imbalanced ({direction_ratio:.1f}x)"
                        balance_color = "inverse"
                    elif direction_ratio > 1.5:
                        balance_status = f"⚖️ Moderate ({direction_ratio:.1f}x)"
                        balance_color = "normal"
                    else:
                        balance_status = "✅ Balanced"
                        balance_color = "normal"

                    st.metric(
                        label="Direction Balance",
                        value=balance_status,
                        delta=f"Total: {int(total_dir * 60)} cars/hr",
                        delta_color=balance_color,
                        help=f"Traffic distribution between directions. Ratio: {direction_ratio:.2f}"
                    )

                # Add a note about direction balance if imbalanced
                if direction_ratio > 2:
                    st.warning(f"⚠️ **Direction Imbalance Detected**: One direction has {direction_ratio:.1f}x more traffic than the other. Consider adjusting light timing to balance flow and reduce congestion.")

            # Show success message
            if has_directions:
                st.success(
                    f"**✅ AI Predictions Active** | Models trained on 18,701 15-minute intervals (from 222,402 measurements, 12 months) from Fulda, Germany. "
                    f"Separate models for Direction 1 and Direction 2. Predicting next 15 minutes. Predictions refresh every 15 minutes."
                )
            else:
                st.success(
                    f"**✅ AI Predictions Active** | Model trained on 18,701 15-minute intervals (from 222,402 measurements, 12 months) from Fulda, Germany. "
                    f"Predicting next 15 minutes. Predictions refresh every 15 minutes."
                )
            st.markdown("---")
        else:
            st.warning("⚠️ AI model loaded but could not generate predictions.")
            st.markdown("---")
    except Exception as e:
        st.warning(f"⚠️ Could not load AI predictions: {str(e)[:100]}")
        st.markdown("---")
else:
    st.info("**ℹ️ AI Model not trained yet.** Run `python model.py` to train on real data.")
    st.markdown("---")

# ============================================================================
# TRAFFIC STATISTICS SECTION
# ============================================================================
if os.path.exists(MODEL_PATH):
    st.markdown("---")
    st.markdown("### 📊 Traffic Statistics & Patterns")

    stats = get_traffic_statistics()

    if stats:
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

        with col_stat1:
            st.metric(
                label="Average Traffic",
                value=f"{stats['avg_traffic']} cars/hr",
                help="Average traffic volume across all hours"
            )

        with col_stat2:
            st.metric(
                label="Peak Hour",
                value=f"{stats['peak_hour']:02d}:00",
                delta=f"{stats['peak_traffic']} cars/hr",
                help=f"Hour with highest average traffic: {stats['peak_hour']:02d}:00"
            )

        with col_stat3:
            st.metric(
                label="Weekday Average",
                value=f"{stats['weekday_avg']} cars/hr",
                help="Average traffic on weekdays"
            )

        with col_stat4:
            st.metric(
                label="Weekend Average",
                value=f"{stats['weekend_avg']} cars/hr",
                delta=f"{stats['weekend_avg'] - stats['weekday_avg']:+d} vs weekday",
                delta_color="normal" if stats['weekend_avg'] < stats['weekday_avg'] else "inverse",
                help="Average traffic on weekends"
            )

        # Rush hour and quiet hour information
        col_rush, col_quiet = st.columns(2)

        with col_rush:
            st.markdown("#### 🚦 Rush Hour Times")
            rush_threshold = int(stats['hourly_stats']['mean'].quantile(0.75) * 60)
            st.info(f"**Peak Traffic Hours:** {stats['rush_hours_formatted']}\n\n*Hours with traffic above 75th percentile (> {rush_threshold} cars/hr)*")

        with col_quiet:
            st.markdown("#### 🌙 Quiet Hours")
            quiet_threshold = int(stats['hourly_stats']['mean'].quantile(0.25) * 60)
            st.success(f"**Low Traffic Hours:** {stats['quiet_hours_formatted']}\n\n*Hours with traffic below 25th percentile (< {quiet_threshold} cars/hr)*")

        # Hourly traffic pattern chart
        st.markdown("#### 📈 Average Traffic by Hour of Day")
        chart_data = stats['hourly_stats'][['hour', 'vehicles_per_hour']].copy()
        chart_data.columns = ['Hour', 'Traffic (cars/hr)']
        chart_data['Hour'] = chart_data['Hour'].astype(str).str.zfill(2) + ':00'

        st.bar_chart(chart_data.set_index('Hour')['Traffic (cars/hr)'], use_container_width=True)

        st.caption(f"📊 Based on {TRAINING_DATA_MONTHS} months of historical data from Fulda, Germany")
    else:
        st.info("📊 Statistics will be available once data is loaded.")

# ============================================================================
# FUTURE SYSTEM DEMONSTRATION VIDEO
# ============================================================================
st.markdown("---")
st.markdown("### 🎬 Future System Demonstration")
st.markdown('<p style="color: #4a5568; font-size: 0.95rem; margin-bottom: 1rem;">Watch how the EcoFlow system could theoretically react in the future with more datapoints and enhanced capabilities:</p>', unsafe_allow_html=True)

# Video file path - local file or URL
# Supports YouTube, Vimeo, or direct video file paths/URLs
VIDEO_URL = "Future_Video.mov"  # Local video file

if VIDEO_URL and os.path.exists(VIDEO_URL):
    # Check if it's a YouTube URL
    if "youtube.com" in VIDEO_URL or "youtu.be" in VIDEO_URL:
        # Extract video ID for YouTube embed
        if "youtube.com/watch?v=" in VIDEO_URL:
            video_id = VIDEO_URL.split("watch?v=")[1].split("&")[0]
        elif "youtu.be/" in VIDEO_URL:
            video_id = VIDEO_URL.split("youtu.be/")[1].split("?")[0]
        else:
            video_id = VIDEO_URL.split("/")[-1]

        st.markdown(f"""
        <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <iframe src="https://www.youtube.com/embed/{video_id}"
                    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowfullscreen>
            </iframe>
        </div>
        """, unsafe_allow_html=True)
    # Check if it's a Vimeo URL
    elif "vimeo.com" in VIDEO_URL:
        video_id = VIDEO_URL.split("/")[-1].split("?")[0]
        st.markdown(f"""
        <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <iframe src="https://player.vimeo.com/video/{video_id}"
                    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;"
                    allow="autoplay; fullscreen; picture-in-picture"
                    allowfullscreen>
            </iframe>
        </div>
        """, unsafe_allow_html=True)
    # Direct video file (MP4, WebM, MOV, etc.) - local file
    else:
        # Check if it's a local file path
        if os.path.exists(VIDEO_URL):
            st.video(VIDEO_URL)
        else:
            # Assume it's a URL
            st.video(VIDEO_URL)
else:
    # Video file not found
    st.warning(f"⚠️ Video file not found: {VIDEO_URL}")
    st.info("📹 Please ensure the video file exists at the specified path.")

st.markdown("---")

# ============================================================================
# SIDEBAR: SIMULATION CONTROLS
# ============================================================================
st.sidebar.markdown("## 👮 Control Room")
st.sidebar.markdown("**Simulation Parameters**")

# Manual controls for testing (using real AI predictions when available)
sim_traffic = st.sidebar.slider(
    "Traffic Volume (cars/hr)",
    min_value=0,
    max_value=3000,
    value=720,
    step=50,
    help="Predicted number of vehicles per hour (typical: 180-900, rush hour: 1,200-1,800)"
)

sim_aqi = st.sidebar.slider(
    "Air Quality PM10 (µg/m³)",
    min_value=0,
    max_value=100,
    value=20,
    step=5,
    help="Particulate matter PM10 concentration"
)

# Capacity threshold
capacity_threshold = st.sidebar.number_input(
    "Intersection Capacity",
    min_value=500,
    max_value=2000,
    value=1000,
    step=50,
    help="Traffic volume threshold for congestion mode (typical: 800-1,200 cars/hr)"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 About")
st.sidebar.info(
    "**EcoFlow** uses AI to predict traffic patterns and "
    "real-time air quality sensors to make intelligent decisions. "
    "\n\n🧠 Prophet ML Model\n"
    "⚙️ Smart Logic Engine\n"
    "🌍 Real SensorBox Data"
)

# ============================================================================
# MAIN DASHBOARD
# ============================================================================
col1, col2 = st.columns([1.2, 1])

# ----------------------------------------------------------------------------
# COLUMN 1: SMART INTERSECTION STATUS
# ----------------------------------------------------------------------------
with col1:
    st.markdown("### 📍 Intersection: Heilbronn Center")

    # Instantiate the logic engine
    intersection = SmartIntersection("Heilbronn Center", capacity_threshold=capacity_threshold)
    status = intersection.decide(sim_traffic, sim_aqi)
    action = intersection.get_action_description()

    # Display status with appropriate styling
    if "REROUTE" in status:
        st.error(f"**{status}**", icon="⛔")
        st.markdown(f"""
        <div class="status-box" style="background: #dc2626; color: #ffffff; border-left: 4px solid #991b1b;">
            <h3 style="color: #ffffff; margin-top: 0; font-weight: 700;">🚨 EMERGENCY ACTION</h3>
            <p style="font-size: 1.2rem; margin: 0.5rem 0; color: #ffffff; font-weight: 500;">{action}</p>
            <hr style="border-color: rgba(255,255,255,0.4); margin: 1rem 0;">
            <p style="color: #ffffff; margin: 0.5rem 0;"><strong>Green Light:</strong> {intersection.green_light_duration}s</p>
            <p style="color: #ffffff; margin: 0.5rem 0;"><strong>Reason:</strong> Air pollution has reached hazardous levels</p>
            <p style="color: #ffffff; margin: 0.5rem 0;"><strong>Action:</strong> Digital road signs directing traffic to alternate routes</p>
        </div>
        """, unsafe_allow_html=True)

    elif "MAX FLOW" in status:
        st.warning(f"**{status}**", icon="⚡")
        st.markdown(f"""
        <div class="status-box" style="background: #f59e0b; color: #ffffff; border-left: 4px solid #d97706;">
            <h3 style="color: #ffffff; margin-top: 0; font-weight: 700;">⚡ HIGH TRAFFIC MODE</h3>
            <p style="font-size: 1.2rem; margin: 0.5rem 0; color: #ffffff; font-weight: 500;">{action}</p>
            <hr style="border-color: rgba(255,255,255,0.4); margin: 1rem 0;">
            <p style="color: #ffffff; margin: 0.5rem 0;"><strong>Green Light:</strong> {intersection.green_light_duration}s (2x standard)</p>
            <p style="color: #ffffff; margin: 0.5rem 0;"><strong>Reason:</strong> Traffic volume exceeds capacity threshold</p>
            <p style="color: #ffffff; margin: 0.5rem 0;"><strong>Action:</strong> Extended green light cycle to maximize throughput</p>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.success(f"**{status}**", icon="✅")
        st.markdown(f"""
        <div class="status-box" style="background: #059669; color: #ffffff; border-left: 4px solid #047857;">
            <h3 style="color: #ffffff; margin-top: 0; font-weight: 700;">✅ NORMAL OPERATION</h3>
            <p style="font-size: 1.2rem; margin: 0.5rem 0; color: #ffffff; font-weight: 500;">{action}</p>
            <hr style="border-color: rgba(255,255,255,0.4); margin: 1rem 0;">
            <p style="color: #ffffff; margin: 0.5rem 0;"><strong>Green Light:</strong> {intersection.green_light_duration}s</p>
            <p style="color: #ffffff; margin: 0.5rem 0;"><strong>Reason:</strong> Traffic and air quality within normal parameters</p>
            <p style="color: #ffffff; margin: 0.5rem 0;"><strong>Action:</strong> Standard traffic light timing</p>
        </div>
        """, unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# COLUMN 2: LIVE METRICS
# ----------------------------------------------------------------------------
with col2:
    st.markdown("### 📊 Live Sensor Metrics")

    # Traffic metric
    traffic_delta = sim_traffic - capacity_threshold
    st.metric(
        label="🚗 Predicted Traffic",
        value=f"{sim_traffic} cars/h",
        delta=f"{traffic_delta:+d} vs capacity",
        delta_color="inverse"
    )

    # Air quality metric
    health_impact = calculate_health_impact(sim_aqi)
    aqi_delta = 50 - sim_aqi  # Distance from WHO threshold
    st.metric(
        label="🌫️ Air Quality (PM10)",
        value=f"{sim_aqi} µg/m³",
        delta=f"{aqi_delta:+.0f} to limit",
        delta_color="normal"
    )

    # Health impact indicator
    st.markdown(f"""
    <div class="status-box" style="background-color: {health_impact['color']}; color: #ffffff; border-left: 4px solid rgba(0,0,0,0.2);">
        <h4 style="margin-top: 0; color: #ffffff; font-weight: 600;">Health Impact: {health_impact['level']}</h4>
        <p style="margin: 0; color: #ffffff;">{health_impact['message']}</p>
    </div>
    """, unsafe_allow_html=True)

    # System info
    st.markdown("### ⚙️ System Status")
    st.info(f"""
    **AI Model:** {'✅ Active' if os.path.exists(MODEL_PATH) else '⚠️ Not Trained'}
    **Logic Engine:** ✅ Active
    **Data Source:** SensorBox Network
    **Last Update:** {datetime.now().strftime('%H:%M:%S')}
    """)

# ============================================================================
# GET GERMAN DEVICE LOCATION
# ============================================================================
@st.cache_data(ttl=3600)
def get_german_sensor_location():
    """
    Get the actual GPS coordinates of the German sensor from the database.
    Falls back to known location coordinates if GPS not available in database.
    """
    GERMAN_IMEI = "865583044299336"

    # Known coordinates for locations mentioned in database
    FULDA_COORDS = {
        'latitude': 50.5528,
        'longitude': 9.6806
    }

    try:
        from config import DB_CONFIG
        conn = psycopg2.connect(**DB_CONFIG)

        query = """
        SELECT
            imei,
            friendly_name,
            location_name,
            location,
            latitude,
            longitude
        FROM device_mapping
        WHERE imei = %s
        """

        df = pd.read_sql(query, conn, params=(GERMAN_IMEI,))
        conn.close()

        if len(df) > 0:
            # Check if GPS coordinates are available
            if df.iloc[0]['latitude'] is not None and pd.notna(df.iloc[0]['latitude']):
                location = {
                    'latitude': float(df.iloc[0]['latitude']),
                    'longitude': float(df.iloc[0]['longitude']),
                    'friendly_name': df.iloc[0]['friendly_name'],
                    'location_name': df.iloc[0]['location_name'] or df.iloc[0]['location'],
                    'source': 'database_gps'
                }
                return location
            # Check if location name indicates Fulda
            elif df.iloc[0]['location'] and 'FULDA' in str(df.iloc[0]['location']).upper():
                location = {
                    'latitude': FULDA_COORDS['latitude'],
                    'longitude': FULDA_COORDS['longitude'],
                    'friendly_name': df.iloc[0]['friendly_name'],
                    'location_name': 'Fulda, Germany',
                    'source': 'database_location_field'
                }
                return location
            else:
                # Device found but no location info
                return {
                    'latitude': HEILBRONN_COORDS['latitude'],
                    'longitude': HEILBRONN_COORDS['longitude'],
                    'friendly_name': df.iloc[0]['friendly_name'],
                    'location_name': None,
                    'source': 'fallback'
                }
        else:
            # Device not found
            return {
                'latitude': HEILBRONN_COORDS['latitude'],
                'longitude': HEILBRONN_COORDS['longitude'],
                'friendly_name': None,
                'location_name': None,
                'source': 'fallback'
            }
    except (psycopg2.OperationalError, psycopg2.Error, ImportError):
        # Database not available or connection failed
        return {
            'latitude': HEILBRONN_COORDS['latitude'],
            'longitude': HEILBRONN_COORDS['longitude'],
            'friendly_name': None,
            'location_name': None,
            'source': 'fallback'
        }
    except Exception:
        # Any other error
        return {
            'latitude': HEILBRONN_COORDS['latitude'],
            'longitude': HEILBRONN_COORDS['longitude'],
            'friendly_name': None,
            'location_name': None,
            'source': 'fallback'
        }

# ============================================================================
# MAP VISUALIZATION
# ============================================================================
st.markdown("---")
st.markdown("### 🗺️ Primary Sensor Location")

col_map1, col_map2 = st.columns([2, 1])

with col_map1:
    # Get the actual German sensor location
    sensor_location = get_german_sensor_location()

    map_df = pd.DataFrame({
        'lat': [sensor_location['latitude']],
        'lon': [sensor_location['longitude']]
    })
    st.map(map_df, zoom=11)

    if sensor_location['source'] in ['database_gps', 'database_location_field']:
        location_text = f"📍 {sensor_location['friendly_name'] or 'German Traffic Sensor'}"
        if sensor_location['location_name']:
            location_text += f" - {sensor_location['location_name']}"
        st.caption(location_text)
    else:
        st.caption("📍 German Traffic Sensor (Training Data Source) - Approximate location (Heilbronn area)")

with col_map2:
    st.markdown("**🎯 Sensor Information**")
    st.metric("Training Device", "1 (Germany)")
    st.metric("Data Period", "12 months")
    st.metric("Records", "222,402")

    if sensor_location['source'] == 'database_gps':
        st.success("✅ GPS coordinates from database")
        if sensor_location['friendly_name']:
            st.info(f"**Device:** {sensor_location['friendly_name']}")
        if sensor_location['location_name']:
            st.info(f"**Location:** {sensor_location['location_name']}")
    elif sensor_location['source'] == 'database_location_field':
        st.success("✅ Location identified from database (Fulda, Germany)")
        if sensor_location['friendly_name']:
            st.info(f"**Device:** {sensor_location['friendly_name']}")
        if sensor_location['location_name']:
            st.info(f"**Location:** {sensor_location['location_name']}")
    else:
        st.warning("⚠️ Using approximate location (database unavailable)")

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #4a5568; padding: 2rem;">
    <p style="color: #2d3748; font-weight: 600;"><strong>🚦 Project EcoFlow</strong> | Future City Hackathon 2025 Heilbronn</p>
    <p style="color: #4a5568;">Smart Traffic Control for Climate-Conscious Cities</p>
    <p style="font-size: 0.9rem; color: #718096;">Powered by SensorBox IoT Network • Prophet ML • Streamlit</p>
</div>
""", unsafe_allow_html=True)
