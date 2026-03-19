"""
game.py — EcoPersona AI
Gamification engine: points, streaks, levels, and badges.
"""

import streamlit as st
from datetime import date, timedelta


# ── Level Thresholds ───────────────────────────────────────────────────────
LEVELS = [
    {"name": "🌱 Beginner",          "min": 0,    "max": 39},
    {"name": "🔍 Aware Explorer",    "min": 40,   "max": 54},
    {"name": "🌿 Green Citizen",     "min": 55,   "max": 69},
    {"name": "⚡ Eco Champion",      "min": 70,   "max": 84},
    {"name": "🌍 Planet Protector",  "min": 85,   "max": 100},
]

# ── All Badges ─────────────────────────────────────────────────────────────
ALL_BADGES = [
    {
        "id": "first_scan",
        "icon": "🔬",
        "name": "First Scan",
        "desc": "Completed your first EcoPersona analysis",
        "points": 50,
        "condition": lambda inputs, score: True,
    },
    {
        "id": "cyclist",
        "icon": "🚲",
        "name": "Pedal Power",
        "desc": "Uses bicycle or walks as primary transport",
        "points": 120,
        "condition": lambda inputs, score: inputs.get("transport") == "bicycle",
    },
    {
        "id": "green_plate",
        "icon": "🥗",
        "name": "Green Plate",
        "desc": "Follows a vegan or vegetarian diet",
        "points": 100,
        "condition": lambda inputs, score: inputs.get("food") in ("vegan", "vegetarian"),
    },
    {
        "id": "energy_saver",
        "icon": "💡",
        "name": "Energy Saver",
        "desc": "Monthly electricity below 200 kWh",
        "points": 150,
        "condition": lambda inputs, score: inputs.get("electricity", 999) < 200,
    },
    {
        "id": "minimalist",
        "icon": "♻️",
        "name": "Minimalist",
        "desc": "Shops only for essential needs",
        "points": 130,
        "condition": lambda inputs, score: inputs.get("shopping") == "minimal",
    },
    {
        "id": "eco_hero",
        "icon": "🏆",
        "name": "Eco Hero",
        "desc": "Achieved an Eco Score of 75 or above",
        "points": 500,
        "condition": lambda inputs, score: score >= 75,
    },
    {
        "id": "ev_driver",
        "icon": "⚡",
        "name": "EV Driver",
        "desc": "Drives an electric vehicle",
        "points": 90,
        "condition": lambda inputs, score: inputs.get("transport") == "electric",
    },
    {
        "id": "low_mileage",
        "icon": "📍",
        "name": "Low Mileage",
        "desc": "Travels less than 100 km per week",
        "points": 80,
        "condition": lambda inputs, score: inputs.get("distance", 999) < 100,
    },
]


# ── Points Calculation ─────────────────────────────────────────────────────
def calculate_points(score, impact_level):
    """Award EcoPoints based on score + impact level bonus."""
    base    = score * 12
    bonus   = {"Low": 300, "Medium": 150, "High": 0}.get(impact_level, 0)
    return base + bonus


# ── Level Detection ────────────────────────────────────────────────────────
def get_level(score):
    """Return current level dict and progress % to next level."""
    for i, lvl in enumerate(LEVELS):
        if lvl["min"] <= score <= lvl["max"]:
            span     = lvl["max"] - lvl["min"]
            progress = round((score - lvl["min"]) / span * 100) if span > 0 else 100
            next_lvl = LEVELS[i + 1]["name"] if i + 1 < len(LEVELS) else None
            return {
                "current": lvl["name"],
                "next": next_lvl,
                "progress": progress,
                "index": i,
            }
    return {"current": LEVELS[-1]["name"], "next": None, "progress": 100, "index": 4}


# ── Badge Evaluation ───────────────────────────────────────────────────────
def evaluate_badges(inputs, score):
    """
    Evaluate all badges against current inputs and score.
    Returns list of badge dicts with 'unlocked' boolean added.
    """
    result = []
    for badge in ALL_BADGES:
        try:
            unlocked = badge["condition"](inputs, score)
        except Exception:
            unlocked = False
        result.append({**badge, "unlocked": unlocked})
    return result


# ── Streak Simulation ──────────────────────────────────────────────────────
def get_streak_data(streak_days=5):
    """
    Simulate a weekly streak display.
    Returns list of dicts: {day, done}.
    """
    today   = date.today()
    weekday = today.weekday()          # Mon=0 … Sun=6
    monday  = today - timedelta(days=weekday)
    days    = []
    for i in range(7):
        d = monday + timedelta(days=i)
        days.append({
            "label": d.strftime("%a")[0],
            "date": d,
            "done": i < streak_days and d <= today,
        })
    return days


# ── Render Helpers ─────────────────────────────────────────────────────────
def render_streak(streak_days=5):
    """Render the weekly streak bar in Streamlit."""
    days = get_streak_data(streak_days)
    cols = st.columns(7)
    for col, day in zip(cols, days):
        with col:
            if day["done"]:
                st.markdown(
                    f"<div style='text-align:center;background:#22c55e;color:#0a0f0a;"
                    f"border-radius:8px;padding:6px 0;font-weight:700;font-size:0.8rem'>"
                    f"{day['label']}<br>✓</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<div style='text-align:center;background:#1e271e;color:#4ade80;"
                    f"border-radius:8px;padding:6px 0;font-size:0.8rem'>"
                    f"{day['label']}<br>·</div>",
                    unsafe_allow_html=True,
                )


def render_badges(badges):
    """Render badge grid in Streamlit."""
    cols = st.columns(4)
    for i, badge in enumerate(badges):
        with cols[i % 4]:
            opacity = "1" if badge["unlocked"] else "0.35"
            border  = "#22c55e" if badge["unlocked"] else "#1e271e"
            st.markdown(
                f"<div style='text-align:center;background:#0f1a0f;border:1px solid {border};"
                f"border-radius:12px;padding:1rem 0.5rem;opacity:{opacity};margin-bottom:8px'>"
                f"<div style='font-size:2rem'>{badge['icon']}</div>"
                f"<div style='font-size:0.7rem;font-weight:600;color:#f0fdf0;margin-top:6px'>{badge['name']}</div>"
                f"<div style='font-size:0.65rem;color:#86efac;margin-top:4px'>{badge['desc']}</div>"
                f"<div style='font-size:0.7rem;color:#4ade80;font-weight:700;margin-top:6px'>"
                f"{'🔓 +' + str(badge['points']) + ' pts' if badge['unlocked'] else '🔒 Locked'}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
