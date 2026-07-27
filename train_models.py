"""
Training Models 
"""

import sys
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

from config import MIN_ROWS_FOR_ML, PM25_MODEL_PATH, PM25_MODEL_META_PATH
from db import load_dataframe

FEATURE_COLUMNS = ["temp_c", "humidity", "pressure", "pm10", "hour_of_day", "day_of_week"]
TARGET_COLUMN = "pm25"


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hour_of_day"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    return df


def time_based_split(df: pd.DataFrame, test_frac: float = 0.2):
    split_idx = int(len(df) * (1 - test_frac))
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]
    return train_df, test_df


def evaluate(model, X_test, y_test) -> dict:
    preds = model.predict(X_test)
    return {
        "mae": float(mean_absolute_error(y_test, preds)),
        "rmse": float(np.sqrt(mean_squared_error(y_test, preds))),
        "r2": float(r2_score(y_test, preds)),
    }


def run_shap_summary(model, X_train, feature_names):
    """Best-effort SHAP summary; skipped gracefully if shap isn't usable."""
    try:
        import shap
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_train)

        plt.figure()
        shap.summary_plot(shap_values, X_train, feature_names=feature_names, show=False)
        out_path = PM25_MODEL_PATH.parent / "shap_summary.png"
        plt.tight_layout()
        plt.savefig(out_path, dpi=150)
        plt.close()
        print(f"SHAP summary plot saved to {out_path}")
    except Exception as e:
        print(f"Skipping SHAP summary (non-fatal): {e}")


def main():
    df = load_dataframe()

    if len(df) < MIN_ROWS_FOR_ML:
        print(
            f"Only {len(df)} rows available, need at least {MIN_ROWS_FOR_ML} "
            f"to train. Skipping — run this again once more data has "
            f"accumulated (pipeline.py runs hourly)."
        )
        sys.exit(0)

    df = engineer_features(df)
    df = df.dropna(subset=FEATURE_COLUMNS + [TARGET_COLUMN]).reset_index(drop=True)

    if len(df) < MIN_ROWS_FOR_ML:
        print(
            f"After dropping rows with missing fields, only {len(df)} usable "
            f"rows remain (need {MIN_ROWS_FOR_ML}). Skipping."
        )
        sys.exit(0)

    train_df, test_df = time_based_split(df)
    X_train, y_train = train_df[FEATURE_COLUMNS], train_df[TARGET_COLUMN]
    X_test, y_test = test_df[FEATURE_COLUMNS], test_df[TARGET_COLUMN]

    print(f"Training on {len(train_df)} rows, testing on {len(test_df)} rows")

    rf = RandomForestRegressor(n_estimators=300, max_depth=None, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    rf_metrics = evaluate(rf, X_test, y_test)
    print("RandomForest:", rf_metrics)

    xgb = XGBRegressor(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
    )
    xgb.fit(X_train, y_train)
    xgb_metrics = evaluate(xgb, X_test, y_test)
    print("XGBoost:", xgb_metrics)

    # Lower RMSE wins
    if rf_metrics["rmse"] <= xgb_metrics["rmse"]:
        best_name, best_model, best_metrics = "random_forest", rf, rf_metrics
    else:
        best_name, best_model, best_metrics = "xgboost", xgb, xgb_metrics

    print(f"\nBest model: {best_name} -> {best_metrics}")

    joblib.dump(best_model, PM25_MODEL_PATH)
    meta = {
        "model_name": best_name,
        "features": FEATURE_COLUMNS,
        "target": TARGET_COLUMN,
        "metrics": {"random_forest": rf_metrics, "xgboost": xgb_metrics},
        "n_train_rows": len(train_df),
        "n_test_rows": len(test_df),
    }
    joblib.dump(meta, PM25_MODEL_META_PATH)
    with open(PM25_MODEL_PATH.parent / "pm25_model_meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    print(f"Saved model to {PM25_MODEL_PATH}")
    print(f"Saved metadata to {PM25_MODEL_META_PATH}")

    run_shap_summary(best_model, X_train, FEATURE_COLUMNS)


if __name__ == "__main__":
    main()
