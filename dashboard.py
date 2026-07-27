from flask import Blueprint, jsonify
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from graphs import get_recent_data
from heat_risk import estimate_heatwave_risk
from ml.footprint_scoring import compute_footprint

dashboard_bp = Blueprint("dashboard", __name__)


def get_current_conditions():
    records = get_recent_data(hours=1)
    latest = records[-1] if records else {}

    env_result = compute_footprint(latest)

    return {
        "weather": {
            "temperature": {"value": latest.get("temp_c"), "unit": "°C"},
            "humidity": {"value": latest.get("humidity"), "unit": "%"},
            "pressure": {"value": latest.get("pressure"), "unit": "hPa"},
            "wind_speed": {"value": latest.get("wind_speed"), "unit": "km/h"},
            "wind_direction": {"value": latest.get("wind_direction"), "unit": "°"},
            "rainfall": {"value": latest.get("rain"), "unit": "mm"},
            "cloud_cover": {"value": latest.get("cloud_cover"), "unit": "%"},
        },
        "air_quality": {
            "pm2_5": {"value": latest.get("pm25"), "unit": "µg/m³"},
            "pm10": {"value": latest.get("pm10"), "unit": "µg/m³"},
            "co": {"value": latest.get("co"), "unit": "ppm"},
            "no2": {"value": latest.get("no2"), "unit": "µg/m³"},
            "so2": {"value": latest.get("so2"), "unit": "µg/m³"},
            "aqi_category": env_result.aqi_category,
        },
        "environmental_risk_score": env_result.footprint_score,
        "environmental_risk_category": env_result.footprint_category,
        "heatwave_risk": estimate_heatwave_risk(latest.get("temp_c"), latest.get("humidity")),
    }


@dashboard_bp.route("/api/dashboard")
def get_dashboard():
    return jsonify(get_current_conditions())


@dashboard_bp.route("/api/trend/<metric>")
def get_trend(metric):
    records = get_recent_data(hours=24)
    points = [{"day": r["timestamp"].strftime("%H:%M"), "value": r.get(metric)} for r in records]
    return jsonify(points)