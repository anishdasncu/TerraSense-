

import sys

import joblib
import pandas as pd
from prophet import Prophet

from config import MIN_ROWS_FOR_PROPHET, PROPHET_MODEL_PATH, MODEL_DIR
from db import load_dataframe

FORECAST_HORIZON_HOURS = 72


def main():
    df = load_dataframe()

    if len(df) < MIN_ROWS_FOR_PROPHET:
        print(
            f"Only {len(df)} rows available, need at least "
            f"{MIN_ROWS_FOR_PROPHET} (~3 weeks hourly) for a reliable "
            f"Prophet forecast. Skipping for now."
        )
        sys.exit(0)

    prophet_df = df[["timestamp", "pm25"]].rename(columns={"timestamp": "ds", "pm25": "y"})
    prophet_df["ds"] = pd.to_datetime(prophet_df["ds"]).dt.tz_localize(None)
    prophet_df = prophet_df.dropna(subset=["y"])

    model = Prophet(
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=False,  
    )
    model.fit(prophet_df)

    future = model.make_future_dataframe(periods=FORECAST_HORIZON_HOURS, freq="h")
    forecast = model.predict(future)

    joblib.dump(model, PROPHET_MODEL_PATH)
    forecast.to_csv(MODEL_DIR / "prophet_forecast.csv", index=False)

    try:
        import matplotlib
        matplotlib.use("Agg")
        fig = model.plot(forecast)
        fig.savefig(MODEL_DIR / "prophet_forecast.png", dpi=150)
        print(f"Forecast plot saved to {MODEL_DIR / 'prophet_forecast.png'}")
    except Exception as e:
        print(f"Skipping plot (non-fatal): {e}")

    print(f"Prophet model saved to {PROPHET_MODEL_PATH}")
    print(f"Forecast (last {FORECAST_HORIZON_HOURS} rows):")
    print(forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(FORECAST_HORIZON_HOURS))


if __name__ == "__main__":
    main()
