import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="London EV Priority Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# GLOBAL STYLING (TEAL / PROFESSIONAL THEME)
# -------------------------------------------------
st.markdown("""
<style>

/* App background */
.main {
    background: linear-gradient(135deg, #0f172a, #1e293b, #0f172a);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a, #1e293b);
}

/* Main page headings */
h1 {
    font-size: 44px !important;
    font-weight: 800 !important;
    background: linear-gradient(90deg, #26c6da, #00acc1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Sub headings */
h2, h3 {
    color: #e2f8fb !important;
    font-weight: 700 !important;
}

/* Normal text */
p, li {
    color: #dbeafe !important;
    font-size: 17px !important;
}

/* Card containers */
.card {
    background: rgba(255,255,255,0.06);
    border-radius: 18px;
    padding: 28px;
    margin-bottom: 28px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.35);
}

/* Metrics */
div[data-testid="metric-container"] {
    background: rgba(38,198,218,0.15);
    border-radius: 14px;
    padding: 16px;
    color: white;
}

/* Sidebar text */
div[role="radiogroup"] label {
    color: #e5e7eb !important;
    font-size: 15px !important;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
st.sidebar.markdown(
    "<h2 style='color:#26c6da;'>EV Priority Dashboard</h2>",
    unsafe_allow_html=True
)

menu = st.sidebar.radio(
    "Navigation",
    [
        "Home / Project Introduction",
        "Priority Prediction (DNN)",
        "Smart Placement Map",
        "Top-10 High Priority Boroughs",
        "Top-10 Medium Priority Boroughs",
        "Top-10 Low Priority Boroughs"
    ]
)

# -------------------------------------------------
# DATA LOADER
# -------------------------------------------------
@st.cache_data
def load_priority_data():
    df = pd.read_csv("ev_priority_predictions.csv")
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df["priority_score"] = pd.to_numeric(df["priority_score"], errors="coerce")
    return df.dropna(subset=["borough", "priority_score"])

df = load_priority_data()

# -------------------------------------------------
# PRIORITY LOGIC
# -------------------------------------------------
def assign_priority(score):
    if score >= 0.15:
        return "High"
    elif score >= 0.08:
        return "Medium"
    else:
        return "Low"

df["priority_label"] = df["priority_score"].apply(assign_priority)

# -------------------------------------------------
# HOME PAGE
# -------------------------------------------------
if menu == "Home / Project Introduction":

    st.markdown("<h1>Smart EV Charging Station Placement – London</h1>", unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
    <h3>📌 Project Overview</h3>
    <p>
    This project presents a <b>data-driven decision support system</b> for identifying
    <b>high-priority EV charging infrastructure locations</b> across Greater London.
    </p>
    </div>

    <div class="card">
    <h3>🎯 Objectives</h3>
    <ul>
        <li>Predict EV charging priority using a <b>Deep Neural Network (DNN)</b></li>
        <li>Support <b>urban planners and policymakers</b></li>
        <li>Provide <b>clear, interpretable insights</b> for infrastructure planning</li>
    </ul>
    </div>

    <div class="card">
    <h3>🧠 Core Technologies</h3>
    <ul>
        <li>Deep Neural Network (Regression)</li>
        <li>Borough-level spatial aggregation</li>
        <li>Interactive decision dashboard (Streamlit)</li>
    </ul>
    <p><b>This dashboard is designed for policy-level decision making.</b></p>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------
# PRIORITY PREDICTION PAGE
# -------------------------------------------------
elif menu == "Priority Prediction (DNN)":

    st.markdown("<h1>Priority Prediction using Deep Neural Network (DNN)</h1>", unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
    <p>
    The DNN predicts a <b>continuous priority score</b> for each EV charging station
    using spatial, infrastructure, and demand-related features.
    </p>
    </div>

    <div class="card">
    <h3>🚦 Priority Thresholds</h3>
    <ul>
        <li>🔴 <b>High Priority</b>: score ≥ 0.15</li>
        <li>🟠 <b>Medium Priority</b>: 0.08 – 0.15</li>
        <li>🟢 <b>Low Priority</b>: &lt; 0.08</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("R² Score", "≈ 0.99")
    col2.metric("MAE", "≈ 0.002")
    col3.metric("RMSE", "≈ 0.002")

# -------------------------------------------------
# SMART PLACEMENT MAP
# -------------------------------------------------
elif menu == "Smart Placement Map":

    st.markdown("<h1>Smart EV Charging Station Placement – London</h1>", unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
    <p>
    This map visualises <b>borough-level EV charging priority zones</b> across Greater London.
    It represents the <b>primary spatial output</b> of the project.
    </p>
    </div>
    """, unsafe_allow_html=True)

    df_agg = (
        df.groupby(["borough", "priority_label"], as_index=False)
        .agg(
            latitude=("latitude", "mean"),
            longitude=("longitude", "mean"),
            priority_score=("priority_score", "mean")
        )
    )

    fig = px.scatter_mapbox(
        df_agg,
        lat="latitude",
        lon="longitude",
        color="priority_label",
        size="priority_score",
        color_discrete_map={
            "High": "red",
            "Medium": "orange",
            "Low": "green"
        },
        hover_name="borough",
        hover_data={"priority_score": True},
        zoom=10,
        height=800
    )

    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_center={"lat": 51.5074, "lon": -0.1278},
        margin=dict(l=0, r=0, t=0, b=0)
    )

    st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------
# 🏆 TOP-10 HIGH PRIORITY BOROUGHS
# -------------------------------------------------
elif menu == "Top-10 High Priority Boroughs":

    st.markdown("<h1 style='color:#ef5350;'>🏆 Top-10 High Priority Boroughs</h1>", unsafe_allow_html=True)

    df_high = df[df["priority_label"] == "High"]

    top10 = (
        df_high.groupby("borough")
        .agg(
            avg_priority_score=("priority_score", "mean"),
            station_count=("priority_score", "count")
        )
        .sort_values("avg_priority_score", ascending=False)
        .head(10)
        .reset_index()
    )

    top10["Suggested Action"] = "Immediate infrastructure expansion"

    st.dataframe(
        top10.style
        .background_gradient(cmap="Reds")
        .format({"avg_priority_score": "{:.3f}"}),
        use_container_width=True
    )

# -------------------------------------------------
# 🟠 TOP-10 MEDIUM PRIORITY BOROUGHS
# -------------------------------------------------
elif menu == "Top-10 Medium Priority Boroughs":

    st.markdown("<h1 style='color:#ffb74d;'> Top-10 Medium Priority Boroughs</h1>", unsafe_allow_html=True)

    df_medium = df[df["priority_label"] == "Medium"]

    top10 = (
        df_medium.groupby("borough")
        .agg(
            avg_priority_score=("priority_score", "mean"),
            station_count=("priority_score", "count")
        )
        .sort_values("avg_priority_score", ascending=False)
        .head(10)
        .reset_index()
    )

    top10["Suggested Action"] = "Monitor and phased upgrades"

    st.dataframe(
        top10.style
        .background_gradient(cmap="Oranges")
        .format({"avg_priority_score": "{:.3f}"}),
        use_container_width=True
    )

# -------------------------------------------------
# 🟢 TOP-10 LOW PRIORITY BOROUGHS
# -------------------------------------------------
elif menu == "Top-10 Low Priority Boroughs":

    st.markdown("<h1 style='color:#66bb6a;'> Top-10 Low Priority Boroughs</h1>", unsafe_allow_html=True)

    df_low = df[df["priority_label"] == "Low"]

    top10 = (
        df_low.groupby("borough")
        .agg(
            avg_priority_score=("priority_score", "mean"),
            station_count=("priority_score", "count")
        )
        .sort_values("avg_priority_score", ascending=True)
        .head(10)
        .reset_index()
    )

    top10["Suggested Action"] = "No immediate action required"

    st.dataframe(
        top10.style
        .background_gradient(cmap="Greens")
        .format({"avg_priority_score": "{:.3f}"}),
        use_container_width=True
    )