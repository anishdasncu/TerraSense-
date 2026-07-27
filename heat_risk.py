def calculate_heat_index(temp_c, humidity):
    """
    NOAA/NWS heat index formula (Rothfusz regression) — the same
    calculation real weather services use to issue heat warnings.
    Combines temperature + humidity into a single 'feels like' value,
    which is more accurate than judging risk off temperature alone.
    """
    temp_f = temp_c * 9 / 5 + 32

    if temp_f < 80:
        return temp_f

    T, R = temp_f, humidity

    hi = (
        -42.379 + 2.04901523 * T + 10.14333127 * R
        - 0.22475541 * T * R - 0.00683783 * T * T
        - 0.05481717 * R * R + 0.00122874 * T * T * R
        + 0.00085282 * T * R * R - 0.00000199 * T * T * R * R
    )

    if R < 13 and 80 <= T <= 112:
        hi -= ((13 - R) / 4) * ((17 - abs(T - 95)) / 17) ** 0.5
    elif R > 85 and 80 <= T <= 87:
        hi += ((R - 85) / 10) * ((87 - T) / 5)

    return hi


def classify_heat_risk(heat_index_f):
    """
    Official NWS heat index risk categories.
    """
    if heat_index_f < 80:
        return "low"
    if heat_index_f < 90:
        return "moderate"      # NWS: "Caution"
    if heat_index_f < 103:
        return "high"          # NWS: "Extreme Caution"
    if heat_index_f < 125:
        return "very_high"     # NWS: "Danger"
    return "extreme"           # NWS: "Extreme Danger"


def estimate_heatwave_risk(temp_c, humidity):
    if temp_c is None or humidity is None:
        return {"level": "unknown", "reason": "insufficient data (missing temperature or humidity)"}

    heat_index_f = calculate_heat_index(temp_c, humidity)
    level = classify_heat_risk(heat_index_f)
    heat_index_c = round((heat_index_f - 32) * 5 / 9, 1)

    return {
        "level": level,
        "heat_index_c": heat_index_c,
        "reason": f"feels like {heat_index_c}°C (actual {temp_c}°C, {humidity}% humidity)",
    }