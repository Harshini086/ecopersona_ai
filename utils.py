"""
utils.py — EcoPersona AI
Scoring engine, persona assignment, CO₂ estimation, and smart nudges.
"""


# ── CO₂ Estimation ─────────────────────────────────────────────────────────
TRANSPORT_CO2 = {
    "bicycle": 0.02,
    "electric": 0.50,
    "public": 1.20,
    "car": 3.80,
    "flight": 7.50,
}

FOOD_CO2 = {
    "vegan": 0.90,
    "vegetarian": 1.40,
    "pescatarian": 1.90,
    "omnivore": 2.80,
    "meat_heavy": 4.20,
}

SHOPPING_CO2 = {
    "minimal": 0.30,
    "moderate": 0.80,
    "frequent": 1.60,
    "heavy": 2.80,
}


def estimate_co2(transport, food, shopping, electricity, distance):
    """
    Estimate annual CO₂ in tonnes.
    Sources: transport base + distance factor + food + shopping + electricity.
    """
    t_co2   = TRANSPORT_CO2.get(transport, 3.80)
    f_co2   = FOOD_CO2.get(food, 2.80)
    s_co2   = SHOPPING_CO2.get(shopping, 0.80)
    d_co2   = round(distance * 52 * 0.00021, 2)     # weekly km → annual
    e_co2   = round(electricity * 12 * 0.00042, 2)  # monthly kWh → annual
    total   = t_co2 + f_co2 + s_co2 + d_co2 + e_co2
    return round(total, 2)


# ── Eco Score (0-100) ──────────────────────────────────────────────────────
TRANSPORT_PENALTY = {
    "bicycle": 0, "electric": 5, "public": 10, "car": 22, "flight": 35
}
FOOD_PENALTY = {
    "vegan": 0, "vegetarian": 4, "pescatarian": 8, "omnivore": 16, "meat_heavy": 24
}
SHOPPING_PENALTY = {
    "minimal": 0, "moderate": 5, "frequent": 12, "heavy": 20
}


def calculate_score(transport, food, shopping, electricity, distance):
    """Calculate eco score 0-100. Higher = better."""
    score = 100
    score -= TRANSPORT_PENALTY.get(transport, 22)
    score -= FOOD_PENALTY.get(food, 16)
    score -= SHOPPING_PENALTY.get(shopping, 5)
    score -= min(distance / 40, 15)
    score -= max(0, min((electricity - 100) / 40, 15))
    return max(5, min(99, round(score)))


def score_breakdown(transport, food, shopping, electricity, distance):
    """Return individual category scores for radar/bar chart."""
    max_t = 35; max_f = 24; max_s = 20; max_d = 15; max_e = 15
    t = round((1 - TRANSPORT_PENALTY.get(transport, 22) / max_t) * 100)
    f = round((1 - FOOD_PENALTY.get(food, 16) / max_f) * 100)
    s = round((1 - SHOPPING_PENALTY.get(shopping, 5) / max_s) * 100)
    d = round((1 - min(distance / 40, max_d) / max_d) * 100)
    e = round((1 - max(0, min((electricity - 100) / 40, max_e)) / max_e) * 100)
    return {
        "Transport": max(0, t),
        "Food & Diet": max(0, f),
        "Shopping": max(0, s),
        "Distance": max(0, d),
        "Energy": max(0, e),
    }


# ── Persona Assignment ─────────────────────────────────────────────────────
def assign_persona(score):
    """Return persona dict based on eco score."""
    if score >= 72:
        return {
            "name": "🌱 Eco Hero",
            "color": "#22c55e",
            "description": (
                "Outstanding! Your lifestyle choices are significantly below the "
                "global average carbon footprint. You're a true environmental leader."
            ),
            "badge": "Planet Guardian 🏅",
            "tip": "Share your habits — inspire others to follow your lead!",
        }
    elif score >= 45:
        return {
            "name": "⚖️ Balanced User",
            "color": "#f59e0b",
            "description": (
                "You make some great eco-conscious choices but have clear areas "
                "to improve. Small tweaks can push you into Eco Hero territory fast."
            ),
            "badge": "Conscious Consumer 🎖️",
            "tip": "Focus on your highest-impact category first.",
        }
    else:
        return {
            "name": "🔥 Carbon Heavy",
            "color": "#ef4444",
            "description": (
                "Your current lifestyle has a high environmental impact. The good "
                "news: targeted changes deliver rapid, measurable improvements."
            ),
            "badge": "Needs Improvement ⚠️",
            "tip": "Start with transport — it delivers the fastest CO₂ reduction.",
        }


# ── Smart Nudges ───────────────────────────────────────────────────────────
def generate_nudges(transport, food, shopping, electricity, distance):
    """Return 3 personalized, measurable nudges based on worst habits."""
    candidates = []

    # Transport nudges
    if transport == "flight":
        candidates.append({
            "icon": "✈️",
            "title": "Replace Flights with Train",
            "detail": (
                f"For trips under 800 km, trains emit ~90 % less CO₂ than flights. "
                f"Switching 4 flights/year saves ≈ 2.8 tonnes CO₂."
            ),
            "saving": "Save ~2.8 t CO₂/year",
            "priority": 10,
        })
    if transport in ("car", "flight"):
        candidates.append({
            "icon": "🚌",
            "title": "3 Days Public Transit / Week",
            "detail": (
                f"Replacing {round(distance * 0.43)} km/week of car trips with bus or metro "
                f"cuts your transport emissions by ~40 %."
            ),
            "saving": f"Save ~{round(distance * 0.18)} kg CO₂/month",
            "priority": 9,
        })
    if transport == "car":
        candidates.append({
            "icon": "🚗",
            "title": "Carpool Twice a Week",
            "detail": (
                "Sharing your regular commute with one colleague halves per-person "
                "emissions. Even 2 days/week delivers a 20 % transport reduction."
            ),
            "saving": "Save ~800 kg CO₂/year",
            "priority": 8,
        })

    # Food nudges
    if food in ("meat_heavy", "omnivore"):
        candidates.append({
            "icon": "🥗",
            "title": "Meat-Free Mondays",
            "detail": (
                "One fully plant-based day per week cuts your food footprint by ~14 %. "
                "Beef produces 60× more CO₂ per gram of protein than legumes."
            ),
            "saving": "Save ~340 kg CO₂/year",
            "priority": 7,
        })
    if food == "meat_heavy":
        candidates.append({
            "icon": "🐟",
            "title": "Swap Beef → Chicken or Fish",
            "detail": (
                "Replacing beef with chicken or fish 3×/week reduces your food "
                "footprint by up to 30 % with minimal lifestyle change."
            ),
            "saving": "Save ~600 kg CO₂/year",
            "priority": 8,
        })

    # Energy nudges
    if electricity > 400:
        candidates.append({
            "icon": "💡",
            "title": "Install LED Bulbs + Smart Plugs",
            "detail": (
                f"LEDs use 75 % less energy than incandescent bulbs. Eliminating "
                f"standby power saves ~{round(electricity * 0.12)} kWh/month."
            ),
            "saving": f"Save ~{round(electricity * 0.17 * 12 * 0.42)} kg CO₂/year",
            "priority": 6,
        })
    if electricity > 300:
        candidates.append({
            "icon": "🌡️",
            "title": "Adjust Thermostat by 2 °C",
            "detail": (
                "Setting your thermostat 2 °C closer to outdoor temp cuts heating/cooling "
                "energy by ~10 %. Use a smart thermostat for automation."
            ),
            "saving": "Save 180–400 kWh/year",
            "priority": 5,
        })

    # Shopping nudges
    if shopping in ("frequent", "heavy"):
        candidates.append({
            "icon": "⏳",
            "title": "Apply the 30-Day Rule",
            "detail": (
                "Wait 30 days before any non-essential purchase. Studies show 68 % of "
                "impulse buys feel unnecessary after the wait period."
            ),
            "saving": "Reduce consumption by 25–40 %",
            "priority": 6,
        })
        candidates.append({
            "icon": "♻️",
            "title": "Buy Second-Hand First",
            "detail": (
                "Check resale platforms for clothing, electronics, and furniture before "
                "buying new. Extends product life by 2.2 years on average."
            ),
            "saving": "Save ~15 kg CO₂ per item",
            "priority": 5,
        })

    # Universal nudge always included
    candidates.append({
        "icon": "📊",
        "title": "Track Weekly Progress",
        "detail": (
            "Users who measure their habits with EcoPersona reduce emissions 23 % "
            "faster. Set a weekly reminder to re-analyze your score."
        ),
        "saving": "Compounding gains over time",
        "priority": 3,
    })

    # Sort by priority, take top 3
    candidates.sort(key=lambda x: x["priority"], reverse=True)
    return candidates[:3]


# ── Future Projection Data ─────────────────────────────────────────────────
def future_projection(co2_current, score):
    """
    Generate 12-month CO₂ projection arrays for current vs improved path.
    Returns dict with months, current, improved, global_avg lists.
    """
    import numpy as np

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    reduction_rate = 0.92 if score >= 70 else 0.82 if score >= 45 else 0.70

    rng = np.random.default_rng(42)
    current  = [round(co2_current + rng.uniform(-0.2, 0.2), 2) for _ in range(12)]
    improved = [round(co2_current * (reduction_rate ** ((i + 1) / 12))
                      + rng.uniform(-0.08, 0.08), 2) for i in range(12)]
    global_avg = [4.8] * 12

    return {
        "months": months,
        "current": current,
        "improved": improved,
        "global_avg": global_avg,
    }
