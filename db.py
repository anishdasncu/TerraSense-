import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

footprint_history = None
weather_history = None
air_quality_history = None

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    client.admin.command("ping")
    db = client["TerraSense_db"]

    footprint_history = db["footprint_history"]
    weather_history = db["weather_history"]
    air_quality_history = db["air_quality_history"]

    print("[db.py] Connected to MongoDB.")
except Exception as e:
    print(f"[db.py] MongoDB connection failed ({e.__class__.__name__}): {e}")