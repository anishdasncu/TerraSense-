from pymongo import MongoClient
from dotenv import load_dotenv
import plotly.graph_objects as go
from datetime import timedelta
import os

IST_OFFSET = timedelta(hours=5, minutes=30)

load_dotenv()

def get_recent_data(hours=24):
    uri = os.getenv("MONGO_URI")
    client = MongoClient(uri)
    db = client["TerraSense_db"]
    collection = db["hourly_readings"]

    cursor = collection.find().sort("timestamp", -1).limit(hours)
    records = list(cursor)
    records.reverse()  # oldest to newest, so the graph reads left to right
    return records

def build_pm25_chart(records):
    timestamps = [r["timestamp"] for r in records]
    pm25_values = [r.get("pm25") for r in records]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=pm25_values,
        mode="lines+markers",
        name="PM2.5"
    ))
    fig.update_layout(
        title="PM2.5 Levels Over Time",
        xaxis_title="Time",
        yaxis_title="PM2.5 (µg/m³)"
    )
    return fig

def build_temp_chart(records):
    timestamps = [r["timestamp"] + IST_OFFSET for r in records]
    temp_values = [r.get("temp_c") for r in records]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=temp_values,
        mode="lines+markers",
        name="Temperature"
    ))
    fig.update_layout(
        title="Temperature Over Time (IST)",
        xaxis_title="Time (IST)",
        yaxis_title="Temperature (°C)"
    )
    return fig

def build_humidity_chart(records):
    timestamps = [r["timestamp"] + IST_OFFSET for r in records]
    humidity_values = [r.get("humidity") for r in records]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=humidity_values,
        mode="lines+markers",
        name="Humidity"
    ))
    fig.update_layout(
        title="Humidity Over Time (IST)",
        xaxis_title="Time (IST)",
        yaxis_title="Humidity (%)"
    )
    return fig

if __name__ == "__main__":
    data = get_recent_data(hours=24)
    print(f"Fetched {len(data)} records from MongoDB")

    fig = build_pm25_chart(data)
    graph_json = fig.to_json()

    print("Graph JSON generated (first 300 chars):")
    print(graph_json[:300])