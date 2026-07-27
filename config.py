import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")   
DB_NAME = "TerraSense_db"            
COLLECTION_NAME = "hourly_readings"

MIN_ROWS_FOR_ML = 100
MIN_ROWS_FOR_PROPHET = 500

MODEL_DIR = Path(__file__).parent / "models"
MODEL_DIR.mkdir(exist_ok=True)

PM25_MODEL_PATH = MODEL_DIR / "pm25_model.pkl"
PM25_MODEL_META_PATH = MODEL_DIR / "pm25_model_meta.joblib"
PROPHET_MODEL_PATH = MODEL_DIR / "prophet_pm25.joblib"