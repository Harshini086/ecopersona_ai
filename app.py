"""
app.py — EcoPersona AI
Main Streamlit application entry point.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import plotly.graph_objects as go
from model import load_and_train, predict_impact, get_feature_importance
from utils import (
    estimate_co2,
    calculate_score,
    score_breakdown,
    assign_persona,
    generate_nudges,
    future_projection,
)
from game import (
    calculate_points,
    get_level,
    evaluate_badges,
    render_streak,
    render_badges,
)

# ── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EcoPersona AI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Syne:wght@700;800&display=swap');

  html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }

  /* Dark background */
  .stApp { background: #0a0f0a; color: #f0fdf0; }
  section[data-testid="stSidebar"] { background: #111811; border-right: 1px solid rgba(74,222,128,0.15); }

  /* Metric cards */
  [data-testid="metric-container"] {
    background: #0f1a0f;
    border: 1px solid rgba(74,222,128,0.15);
    border-radius: 14px;
    padding: 1rem;
  }
  [data-testid="metric-container"] label { color: #4ade80 !important; font-size: 0.7rem !important; letter-spacing: 2px; text-transform: uppercase; }
  [data-testid="metric-container"] [data-testid="stMetricValue"] { color: #f0fdf0 !important; font-family: 'Syne', sans-serif; font-size: 2rem !important; }
  [data-testid="metric-container"] [data-testid="stMetricDelta"] { font-size: 0.75rem !important; }

  /* Buttons */
  .stButton > button {
    background: #4ade80 !important; color: #0a0f0a !important;
    font-family: 'Syne', sans-serif !important; font-weight: 800 !important;
    border: none !important; border-radius: 10px !important;
    padding: 0.7rem 2rem !important; font-size: 1rem !important;
    transition: all 0.2s !important;
  }
  .stButton > button:hover { background: #22c55e !important; transform: translateY(-2px); }

  /* Progress bar */
  .stProgress > div > div { background: #4ade80 !important; }
  .stProgress { border-radius: 8px; overflow: hidden; }

  /* Selectbox / Slider */
  .stSelectbox > div > div { background: #111811 !important; border: 1px solid rgba(74,222,128,0.2) !important; color: #f0fdf0 !important; }
  .stSlider > div > div > div { color: #4ade80 !important; }

  /* Divider */
  hr { border-color: rgba(74,222,128,0.15) !important; }

  /* Expanders */
  .streamlit-expanderHeader { background: #0f1a0f !important; color: #4ade80 !important; }

  /* Section headers */
  .section-title {
    font-family: 'Syne', sans-serif; font-size: 1.3rem; font-weight: 800;
    color: #f0fdf0; margin-bottom: 0.25rem;
  }
  .section-pill {
    display: inline-block; background: rgba(74,222,128,0.1); color: #4ade80;
    font-size: 0.65rem; letter-spacing: 2px; text-transform: uppercase;
    padding: 3px 10px; border-radius: 4px; font-weight: 600; margin-bottom: 1rem;
  }

  /* Nudge card */
  .nudge-card {
    background: #0f1a0f; border: 1px solid rgba(74,222,128,0.15);
    border-radius: 14px; padding: 1.25rem; margin-bottom: 0.75rem;
    transition: border-color 0.2s;
  }
  .nudge-card:hover { border-color: rgba(74,222,128,0.4); }
  .nudge-num {
    display: inline-flex; align-items: center; justify-content: center;
    width: 26px; height: 26px; background: #4ade80; color: #0a0f0a;
    border-radius: 50%; font-size: 0.75rem; font-weight: 800; margin-bottom: 0.5rem;
  }
  .nudge-title { font-size: 0.95rem; font-weight: 700; color: #f0fdf0; }
  .nudge-detail { font-size: 0.8rem; color: #86efac; line-height: 1.6; margin-top: 0.35rem; }
  .nudge-saving { font-size: 0.72rem; color: #4ade80; font-weight: 600; margin-top: 0.5rem; }

  /* Persona card */
  .persona-card {
    background: #0f1a0f; border: 1px solid rgba(74,222,128,0.2);
    border-radius: 16px; padding: 1.5rem; text-align: center;
  }
  .persona-icon { font-size: 3.5rem; }
  .persona-name { font-family: 'Syne', sans-serif; font-size: 1.6rem; font-weight: 800; margin-top: 0.5rem; }
  .persona-desc { font-size: 0.82rem; color: #86efac; line-height: 1.7; margin-top: 0.5rem; }
  .persona-badge {
    display: inline-block; margin-top: 0.75rem; padding: 4px 14px;
    border-radius: 50px; font-size: 0.75rem; font-weight: 700;
    background: rgba(74,222,128,0.1); color: #4ade80;
  }

  /* Score ring wrapper */
  .ring-wrap { display: flex; justify-content: center; align-items: center; padding: 1rem 0; }
</style>
""", unsafe_allow_html=True)


# ── Cache ML model ─────────────────────────────────────────────────────────
@st.cache_resource
def get_model():
    return load_and_train("data.csv")


# ── Header ─────────────────────────────────────────────────────────────────
col_logo, col_level = st.columns([3, 1])
with col_logo:
    st.markdown(
        "<h1 style='font-family:Syne,sans-serif;font-size:2rem;margin:0;"
        "color:#f0fdf0'><span style='color:#4ade80'>Eco</span>Persona AI</h1>"
        "<p style='color:#86efac;font-size:0.85rem;margin:0'>Environmental Intelligence System</p>",
        unsafe_allow_html=True,
    )

st.markdown("---")


# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='font-family:Syne,sans-serif;font-size:1.2rem;color:#4ade80;"
        "font-weight:800;margin-bottom:0.25rem'>Configure Lifestyle</div>",
        unsafe_allow_html=True,
    )
    st.caption("Adjust inputs to match your habits, then click Analyze.")
    st.markdown("---")

    st.markdown("**🚗 Transport**")
    transport = st.selectbox(
        "Primary transport mode",
        ["bicycle", "electric", "public", "car", "flight"],
        index=3,
        format_func=lambda x: {
            "bicycle": "🚲 Bicycle / Walking",
            "electric": "⚡ Electric Vehicle",
            "public": "🚌 Public Transit",
            "car": "🚗 Petrol/Diesel Car",
            "flight": "✈️ Frequent Flights",
        }[x],
    )
    distance = st.slider("Weekly travel distance (km)", 10, 1000, 200, step=10)

    st.markdown("---")
    st.markdown("**🍽️ Diet & Lifestyle**")
    food = st.selectbox(
        "Food habits",
        ["vegan", "vegetarian", "pescatarian", "omnivore", "meat_heavy"],
        index=3,
        format_func=lambda x: {
            "vegan": "🥦 Vegan",
            "vegetarian": "🥗 Vegetarian",
            "pescatarian": "🐟 Pescatarian",
            "omnivore": "🍽️ Omnivore",
            "meat_heavy": "🥩 Meat-heavy",
        }[x],
    )
    shopping = st.selectbox(
        "Shopping frequency",
        ["minimal", "moderate", "frequent", "heavy"],
        index=1,
        format_func=lambda x: {
            "minimal": "📦 Minimal (needs only)",
            "moderate": "🛒 Moderate",
            "frequent": "🛍️ Frequent shopper",
            "heavy": "💳 Heavy consumer",
        }[x],
    )

    st.markdown("---")
    st.markdown("**⚡ Home Energy**")
    electricity = st.slider("Monthly electricity (kWh)", 50, 1000, 300, step=10)

    st.markdown("---")
    analyze = st.button("🔍 Analyze My EcoPersona", use_container_width=True)

    st.markdown("---")
    st.caption("Model accuracy shown after analysis.")


# ── Main content ───────────────────────────────────────────────────────────
if not analyze:
    st.markdown(
        "<div style='text-align:center;padding:6rem 0'>"
        "<div style='font-size:5rem;opacity:0.5'>🌍</div>"
        "<h2 style='font-family:Syne,sans-serif;color:#86efac;margin:1rem 0 0.5rem'>Know Your Carbon Story</h2>"
        "<p style='color:#4ade80;max-width:400px;margin:0 auto;line-height:1.7'>"
        "Configure your lifestyle in the sidebar and click <strong>Analyze My EcoPersona</strong> "
        "to discover your persona, earn badges, and get smart nudges."
        "</p></div>",
        unsafe_allow_html=True,
    )
    st.stop()


# ── Run analysis ───────────────────────────────────────────────────────────
model, accuracy = get_model()

inputs = {
    "transport": transport,
    "food": food,
    "shopping": shopping,
    "electricity": electricity,
    "distance": distance,
}

impact_level, proba     = predict_impact(model, transport, food, shopping, electricity, distance)
score                   = calculate_score(transport, food, shopping, electricity, distance)
co2                     = estimate_co2(transport, food, shopping, electricity, distance)
persona                 = assign_persona(score)
level_info              = get_level(score)
points                  = calculate_points(score, impact_level)
nudges                  = generate_nudges(transport, food, shopping, electricity, distance)
breakdown               = score_breakdown(transport, food, shopping, electricity, distance)
badges                  = evaluate_badges(inputs, score)
projection              = future_projection(co2, score)
feature_imp             = get_feature_importance(model)

# Model accuracy in sidebar
with st.sidebar:
    st.markdown(
        f"<div style='background:#0f1a0f;border:1px solid rgba(74,222,128,0.2);"
        f"border-radius:10px;padding:0.75rem;text-align:center'>"
        f"<div style='font-size:0.65rem;color:#4ade80;letter-spacing:2px;text-transform:uppercase'>Model Accuracy</div>"
        f"<div style='font-size:1.6rem;font-family:Syne,sans-serif;color:#f0fdf0;font-weight:800'>{accuracy*100:.1f}%</div>"
        f"<div style='font-size:0.65rem;color:#86efac'>Decision Tree Classifier</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

# ═══════════════════════════════════════════════════════════════════════════
# 1 ── HERO STATS
# ═══════════════════════════════════════════════════════════════════════════
st.markdown(
    "<div class='section-title'>Dashboard</div>"
    "<div class='section-pill'>Live Analysis</div>",
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)
delta_color = "normal" if score >= 45 else "inverse"
c1.metric("🌿 Eco Score", f"{score}/100",
          delta=f"{'Above' if score >= 60 else 'Below'} average",
          delta_color=delta_color)
c2.metric("📊 Impact Level", impact_level,
          delta="Low carbon" if impact_level == "Low" else ("Moderate" if impact_level == "Medium" else "High carbon"),
          delta_color="normal" if impact_level == "Low" else ("off" if impact_level == "Medium" else "inverse"))
c3.metric("⚡ EcoPoints", f"{points:,}",
          delta=f"+{round(points*0.08)} this session")
c4.metric("🏭 CO₂ / Year", f"{co2} t",
          delta=f"{'−' if co2 < 4.8 else '+'}{abs(round(co2-4.8,1))} vs global avg",
          delta_color="normal" if co2 < 4.8 else "inverse")

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════
# 2 ── SCORE + PERSONA
# ═══════════════════════════════════════════════════════════════════════════
st.markdown(
    "<div class='section-title'>Score &amp; Persona</div>"
    "<div class='section-pill'>Identity Analysis</div>",
    unsafe_allow_html=True,
)

col_score, col_persona = st.columns(2)

with col_score:
    # Eco Score donut via Plotly
    fig_donut = go.Figure(go.Pie(
        values=[score, 100 - score],
        hole=0.72,
        marker_colors=["#4ade80" if score >= 70 else "#f59e0b" if score >= 45 else "#ef4444", "#1e271e"],
        textinfo="none",
        hoverinfo="skip",
    ))
    fig_donut.add_annotation(
        text=f"<b>{score}</b>",
        x=0.5, y=0.55,
        font_size=44, font_color="#f0fdf0", font_family="Syne",
        showarrow=False,
    )
    fig_donut.add_annotation(
        text="SCORE",
        x=0.5, y=0.38,
        font_size=12, font_color="#4ade80",
        showarrow=False,
    )
    fig_donut.update_layout(
        showlegend=False, margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=240,
    )
    st.plotly_chart(fig_donut, use_container_width=True)

    # Score category breakdown bars
    st.markdown("**Category Breakdown**")
    for cat, val in breakdown.items():
        col_a, col_b = st.columns([1, 3])
        col_a.caption(cat)
        col_b.progress(val / 100)

    # Level progress
    st.markdown("---")
    st.markdown(f"**Level: {level_info['current']}**")
    if level_info["next"]:
        st.progress(level_info["progress"] / 100)
        st.caption(f"{level_info['progress']}% toward {level_info['next']}")
    else:
        st.success("🎉 Maximum level reached — Planet Protector!")

with col_persona:
    impact_color = "#22c55e" if impact_level == "Low" else "#f59e0b" if impact_level == "Medium" else "#ef4444"
    st.markdown(
        f"<div class='persona-card'>"
        f"<div class='persona-icon'>{persona['name'].split()[0]}</div>"
        f"<div class='persona-name' style='color:{persona['color']}'>{' '.join(persona['name'].split()[1:])}</div>"
        f"<div class='persona-desc'>{persona['description']}</div>"
        f"<div class='persona-badge'>{persona['badge']}</div>"
        f"<hr style='border-color:rgba(74,222,128,0.1);margin:1rem 0'>"
        f"<div style='font-size:0.78rem;color:#4ade80;font-style:italic'>💡 {persona['tip']}</div>"
        f"<hr style='border-color:rgba(74,222,128,0.1);margin:1rem 0'>"
        f"<div style='font-size:0.7rem;color:#86efac;letter-spacing:2px;text-transform:uppercase;margin-bottom:0.5rem'>ML Confidence</div>"
        f"<div style='display:flex;justify-content:center;gap:1.5rem'>"
        f"<span style='font-size:0.8rem;color:#22c55e'>Low: {proba[0]*100:.0f}%</span>"
        f"<span style='font-size:0.8rem;color:#f59e0b'>Med: {proba[1]*100:.0f}%</span>"
        f"<span style='font-size:0.8rem;color:#ef4444'>High: {proba[2]*100:.0f}%</span>"
        f"</div></div>",
        unsafe_allow_html=True,
    )

    # Weekly streak
    st.markdown("")
    st.markdown("**🔥 Weekly Streak**")
    render_streak(streak_days=5)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════
# 3 ── FUTURE PROJECTION CHART
# ═══════════════════════════════════════════════════════════════════════════
st.markdown(
    "<div class='section-title'>Future Projection</div>"
    "<div class='section-pill'>12-Month Forecast</div>",
    unsafe_allow_html=True,
)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=projection["months"], y=projection["current"],
    name="Current Path", mode="lines+markers",
    line=dict(color="#ef4444", width=2.5),
    marker=dict(size=6), fill="tozeroy", fillcolor="rgba(239,68,68,0.07)",
))
fig.add_trace(go.Scatter(
    x=projection["months"], y=projection["improved"],
    name="With Smart Nudges", mode="lines+markers",
    line=dict(color="#4ade80", width=2.5),
    marker=dict(size=6), fill="tozeroy", fillcolor="rgba(74,222,128,0.07)",
))
fig.add_trace(go.Scatter(
    x=projection["months"], y=projection["global_avg"],
    name="Global Average (4.8t)", mode="lines",
    line=dict(color="rgba(255,255,255,0.25)", width=1.5, dash="dot"),
))
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#86efac", family="Space Grotesk"),
    legend=dict(orientation="h", y=1.12, font=dict(size=11)),
    xaxis=dict(gridcolor="rgba(74,222,128,0.08)", color="#4ade80"),
    yaxis=dict(gridcolor="rgba(74,222,128,0.08)", color="#4ade80",
               title="CO₂ (tonnes)"),
    margin=dict(t=40, b=20, l=10, r=10),
    height=340,
)
st.plotly_chart(fig, use_container_width=True)

# Savings callout
saved = round(co2 - projection["improved"][-1], 2)
if saved > 0:
    st.success(
        f"✅ Following the smart nudges could reduce your annual CO₂ by **{saved} tonnes** "
        f"— equivalent to planting **{round(saved/0.022)} trees**!"
    )

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════
# 4 ── SMART NUDGES
# ═══════════════════════════════════════════════════════════════════════════
st.markdown(
    "<div class='section-title'>Smart Nudges</div>"
    "<div class='section-pill'>Personalized Actions</div>",
    unsafe_allow_html=True,
)

for i, nudge in enumerate(nudges, 1):
    st.markdown(
        f"<div class='nudge-card'>"
        f"<div class='nudge-num'>{i}</div>"
        f"<div class='nudge-title'>{nudge['icon']} {nudge['title']}</div>"
        f"<div class='nudge-detail'>{nudge['detail']}</div>"
        f"<div class='nudge-saving'>↓ {nudge['saving']}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════
# 5 ── REWARDS & BADGES
# ═══════════════════════════════════════════════════════════════════════════
st.markdown(
    "<div class='section-title'>Badges &amp; Rewards</div>"
    "<div class='section-pill'>Achievements</div>",
    unsafe_allow_html=True,
)

unlocked = [b for b in badges if b["unlocked"]]
locked   = [b for b in badges if not b["unlocked"]]
total_pts = sum(b["points"] for b in unlocked)

b1, b2, b3 = st.columns(3)
b1.metric("🏅 Badges Unlocked", f"{len(unlocked)}/{len(badges)}")
b2.metric("⚡ Badge Points", f"{total_pts:,}")
b3.metric("🔒 Still to Unlock", len(locked))

st.markdown("")
render_badges(badges)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════
# 6 ── FEATURE IMPORTANCE (MODEL INSIGHTS)
# ═══════════════════════════════════════════════════════════════════════════
with st.expander("🔍 Model Insights — Feature Importance"):
    st.caption(f"Decision Tree trained on synthetic dataset · Accuracy: **{accuracy*100:.1f}%**")
    fig2 = go.Figure(go.Bar(
        x=list(feature_imp.values()),
        y=list(feature_imp.keys()),
        orientation="h",
        marker_color=["#4ade80", "#22c55e", "#16a34a", "#15803d", "#166534"],
    ))
    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#86efac", family="Space Grotesk"),
        xaxis=dict(gridcolor="rgba(74,222,128,0.1)", title="Importance Score"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        margin=dict(t=10, b=10, l=10, r=10), height=240,
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── Footer ─────────────────────────────────────────────────────────────────
st.markdown(
    "<div style='text-align:center;color:#4ade80;font-size:0.75rem;padding:2rem 0 0.5rem'>"
    "EcoPersona AI · Built with Streamlit, scikit-learn &amp; Plotly · 🌍"
    "</div>",
    unsafe_allow_html=True,
)
