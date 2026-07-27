from apscheduler.schedulers.blocking import BlockingScheduler
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timezone
import requests
import os

LAT = 28.6139
LON = 77.2090

def fetch_weather():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LAT,
        "longitude": LON,
        "current": "temperature_2m,relative_humidity_2m,surface_pressure,"
                    "wind_speed_10m,wind_direction_10m,rain,cloud_cover"
    }
    resp = requests.get(url, params=params)
    return resp.json()

def fetch_air_quality(api_key):
    """Find the nearest monitoring station."""
    url = "https://api.openaq.org/v3/locations"
    headers = {"X-API-Key": api_key}
    params = {"coordinates": f"{LAT},{LON}", "radius": 25000, "limit": 1}
    resp = requests.get(url, headers=headers, params=params)
    return resp.json()

def fetch_latest_measurements(location_id, api_key):
    url = f"https://api.openaq.org/v3/locations/{location_id}/latest"
    headers = {"X-API-Key": api_key}
    resp = requests.get(url, headers=headers)
    return resp.json()

def clean(weather_raw, air_raw, latest_raw, last_known=None):
    if last_known is None:
        last_known = {}

    current = weather_raw.get("current", {})
    temp_c = current.get("temperature_2m")
    humidity = current.get("relative_humidity_2m")
    pressure = current.get("surface_pressure")
    wind_speed = current.get("wind_speed_10m")
    wind_direction = current.get("wind_direction_10m")
    rain = current.get("rain")
    cloud_cover = current.get("cloud_cover")

    station = air_raw.get("results", [{}])[0]
    sensor_lookup = {
        s["id"]: s["parameter"]["name"]
        for s in station.get("sensors", [])
    }

    # NEW: added co, no2, so2 alongside pm25/pm10
    pollutants = {"pm25": None, "pm10": None, "co": None, "no2": None, "so2": None}

    for reading in latest_raw.get("results", []):
        sensor_id = reading.get("sensorsId")
        param_name = sensor_lookup.get(sensor_id)
        value = reading.get("value")
        if param_name in pollutants:
            pollutants[param_name] = value

    # fall back to last known value for anything missing this round
    fields = {
        "temp_c": temp_c, "humidity": humidity, "pressure": pressure,
        "wind_speed": wind_speed, "wind_direction": wind_direction,
        "rain": rain, "cloud_cover": cloud_cover,
        **pollutants,
    }
    for key, value in fields.items():
        if value is None:
            fields[key] = last_known.get(key)

    doc = {"timestamp": datetime.now(timezone.utc), "city": "Delhi", **fields}
    return doc

load_dotenv()

def save_to_mongo(doc):
    uri = os.getenv("MONGO_URI")
    client = MongoClient(uri)
    db = client["TerraSense_db"]
    collection = db["hourly_readings"]
    result = collection.insert_one(doc)
    print("Inserted document ID:", result.inserted_id)

def get_last_known_values():
    uri = os.getenv("MONGO_URI")
    client = MongoClient(uri)
    db = client["TerraSense_db"]
    collection = db["hourly_readings"]
    last_doc = collection.find_one(sort=[("timestamp", -1)])
    return last_doc or {}

def run_pipeline():
    print(f"\n--- Running pipeline at {datetime.now(timezone.utc)} ---")
    api_key = os.getenv("OPENAQ_API_KEY")

    weather_data = fetch_weather()
    air_data = fetch_air_quality(api_key)

    station = air_data.get("results", [{}])[0]
    location_id = station.get("id")

    latest_data = fetch_latest_measurements(location_id, api_key)
    last_known = get_last_known_values()

    cleaned = clean(weather_data, air_data, latest_data, last_known)
    print("Cleaned document:", cleaned)

    save_to_mongo(cleaned)

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(run_pipeline, 'interval', hours=1)
    print("Scheduler started. Running once immediately, then every hour...")
    run_pipeline()
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped.")