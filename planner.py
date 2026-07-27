from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from db import footprint_history
from routes.dashboard import get_current_conditions

planner_bp = Blueprint("planner", __name__)

HEATING_SCORES = {"gas_electric": 30, "renewable": 10, "none": 0}
FOOD_WASTE_SCORES = {"often": 30, "sometimes": 15, "rarely": 0}
RECYCLING_SCORES = {"never": 50, "sometimes": 25, "always": 0}
PLASTIC_SCORES = {"high": 50, "moderate": 25, "low": 0}
FIXTURE_SCORES = {"none": 30, "some": 15, "all": 0}

CATEGORY_TIPS = {
    "transport": "Try public transport or carpooling 2–3 days a week instead of driving daily.",
    "energy": "Cut AC usage by a couple hours a day, or raise the thermostat by 2°C.",
    "diet": "Try 1–2 meat-free days a week — it's one of the highest-impact changes available.",
    "waste": "Start separating recyclables and cut down on single-use plastic where you can.",
    "water": "Shorten showers by a few minutes and fix any leaks — small habit, real savings.",
}


def score_transport(weekly_car_km, flights_per_year):
    km_score = min(weekly_car_km / 300 * 70, 70)
    flight_score = min(flights_per_year * 6, 30)
    return round(km_score + flight_score)


def score_energy(ac_hours, heating):
    ac_score = min(ac_hours / 10 * 70, 70)
    heating_score = HEATING_SCORES.get(heating, 0)
    return round(ac_score + heating_score)


def score_diet(meat_meals_per_week, food_waste):
    meat_score = min(meat_meals_per_week / 14 * 70, 70)
    waste_score = FOOD_WASTE_SCORES.get(food_waste, 0)
    return round(meat_score + waste_score)


def score_waste(recycling, plastic_use):
    return RECYCLING_SCORES.get(recycling, 0) + PLASTIC_SCORES.get(plastic_use, 0)


def score_water(shower_minutes, fixtures):
    shower_score = min(shower_minutes / 20 * 70, 70)
    fixture_score = FIXTURE_SCORES.get(fixtures, 0)
    return round(shower_score + fixture_score)


def calculate_footprint(answers):
    category_scores = {
        "transport": score_transport(
            float(answers.get("weekly_car_km", 0) or 0),
            float(answers.get("flights_per_year", 0) or 0),
        ),
        "energy": score_energy(
            float(answers.get("ac_hours", 0) or 0),
            answers.get("heating"),
        ),
        "diet": score_diet(
            float(answers.get("meat_meals_per_week", 0) or 0),
            answers.get("food_waste"),
        ),
        "waste": score_waste(
            answers.get("recycling"),
            answers.get("plastic_use"),
        ),
        "water": score_water(
            float(answers.get("shower_minutes", 0) or 0),
            answers.get("fixtures"),
        ),
    }

    overall_score = round(sum(category_scores.values()) / len(category_scores))
    top_factor = max(category_scores, key=category_scores.get)
    recommendation = CATEGORY_TIPS[top_factor]

    conditions = get_current_conditions()

    if top_factor == "transport" and conditions["air_quality"]["aqi_category"] in ("Moderate", "Poor", "Very Poor", "Severe"):
        recommendation += (
            f" Air quality is currently {conditions['air_quality']['aqi_category']} — "
            "cutting car trips today helps your footprint and your lungs."
        )
    if top_factor == "energy" and conditions["heatwave_risk"]["level"] in ("high", "very_high", "extreme"):
        recommendation += (
            " Heat risk is elevated right now, so AC use will spike — try fans or shade "
            "during peak hours instead of cranking the AC."
        )

    return {
        "score": overall_score,
        "category_scores": category_scores,
        "top_factor": top_factor,
        "recommendation": recommendation,
    }


@planner_bp.route("/api/footprint", methods=["POST"])
def submit_footprint():
    body = request.json or {}
    user_id = body.get("user_id")
    answers = body.get("answers", {})

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    result = calculate_footprint(answers)

    if footprint_history is not None:
        footprint_history.insert_one({
            "user_id": user_id,
            "answers": answers,
            "score": result["score"],
            "category_scores": result["category_scores"],
            "top_factor": result["top_factor"],
            "recommendation": result["recommendation"],
            "submitted_at": datetime.now(timezone.utc),
        })
    else:
        result["warning"] = "Not saved — MongoDB connection failed."

    return jsonify(result)