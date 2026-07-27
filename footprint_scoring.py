"""
Step 3: Footprint scoring.

"""


from __future__ import annotations
from dataclasses import dataclass


PM25_BREAKPOINTS = [
    (0, 30, 0, 50),
    (31, 60, 51, 100),
    (61, 90, 101, 200),
    (91, 120, 201, 300),
    (121, 250, 301, 400),
    (251, 380, 401, 500),
]

PM10_BREAKPOINTS = [
    (0, 50, 0, 50),
    (51, 100, 51, 100),
    (101, 250, 101, 200),
    (251, 350, 201, 300),
    (351, 430, 301, 400),
    (431, 600, 401, 500),
]

AQI_CATEGORIES = [
    (0, 50, "Good"),
    (51, 100, "Satisfactory"),
    (101, 200, "Moderate"),
    (201, 300, "Poor"),
    (301, 400, "Very Poor"),
    (401, 500, "Severe"),
]

WEATHER_WEIGHT = 0.30  
AQI_WEIGHT = 1 - WEATHER_WEIGHT


FOOTPRINT_CATEGORIES = [
    (0, 10, "Good"),
    (10, 20, "Satisfactory"),
    (20, 40, "Moderate"),
    (40, 60, "Poor"),
    (60, 80, "Very Poor"),
    (80, 100, "Severe"),
]


def _footprint_category_for(score: float) -> str:
    for lo, hi, label in FOOTPRINT_CATEGORIES:
        if lo <= score <= hi:
            return label
    return "Severe"


@dataclass
class FootprintResult:
    pm25_sub_index: float | None
    pm10_sub_index: float | None
    aqi_score: float | None
    aqi_category: str | None
    weather_stress_score: float
    footprint_score: float | None
    footprint_category: str | None


def _sub_index(concentration: float, breakpoints) -> float:
    """Linear interpolation within the matching CPCB breakpoint band."""
    if concentration is None:
        return None

    for c_low, c_high, i_low, i_high in breakpoints:
        if c_low <= concentration <= c_high:
            return i_low + (concentration - c_low) * (i_high - i_low) / (c_high - c_low)

    c_low, c_high, i_low, i_high = breakpoints[-1]
    if concentration > c_high:
        return i_low + (concentration - c_low) * (i_high - i_low) / (c_high - c_low)
    return 0.0


def _category_for(score: float) -> str:
    for lo, hi, label in AQI_CATEGORIES:
        if lo <= score <= hi:
            return label
    return "Severe"


def _weather_stress_score(temp_c, humidity, pressure) -> float:
    
    components = []

    if temp_c is not None:
        
        if 20 <= temp_c <= 28:
            components.append(0)
        else:
            departure = min(abs(temp_c - 24) - 4, 20)  # cap contribution
            components.append(max(0, departure) * 5)  # scale to ~0-100

    if humidity is not None:
        
        if 30 <= humidity <= 60:
            components.append(0)
        else:
            departure = min(abs(humidity - 45) - 15, 40)
            components.append(max(0, departure) * 2.5)

    if pressure is not None:
        
        if pressure < 1005:
            components.append(min((1005 - pressure) * 4, 100))
        else:
            components.append(0)

    if not components:
        return 0.0

    return min(sum(components) / len(components), 100.0)


def compute_footprint(record: dict) -> FootprintResult:
    
    pm25 = record.get("pm25")
    pm10 = record.get("pm10")

    pm25_idx = _sub_index(pm25, PM25_BREAKPOINTS) if pm25 is not None else None
    pm10_idx = _sub_index(pm10, PM10_BREAKPOINTS) if pm10 is not None else None

    candidate_indices = [i for i in (pm25_idx, pm10_idx) if i is not None]
    aqi_score = max(candidate_indices) if candidate_indices else None
    aqi_category = _category_for(aqi_score) if aqi_score is not None else None

    weather_score = _weather_stress_score(
        record.get("temp_c"), record.get("humidity"), record.get("pressure")
    )

    if aqi_score is not None:
        
        aqi_norm = min(aqi_score / 5, 100)
        footprint_score = AQI_WEIGHT * aqi_norm + WEATHER_WEIGHT * weather_score
        footprint_category = _footprint_category_for(footprint_score)
    else:
        footprint_score = None
        footprint_category = None

    return FootprintResult(
        pm25_sub_index=pm25_idx,
        pm10_sub_index=pm10_idx,
        aqi_score=aqi_score,
        aqi_category=aqi_category,
        weather_stress_score=round(weather_score, 1),
        footprint_score=round(footprint_score, 1) if footprint_score is not None else None,
        footprint_category=footprint_category,
    )


if __name__ == "__main__":
    
    sample_record = {
        "pm25": 145,
        "pm10": 210,
        "temp_c": 34.2,
        "humidity": 68,
        "pressure": 998,
    }
    result = compute_footprint(sample_record)
    print("Sample record:", sample_record)
    print("Result:", result)
