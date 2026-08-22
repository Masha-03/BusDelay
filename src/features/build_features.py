# src/features/build_features.py
import pandas as pd
import holidays


def add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    df["hour"] = df["actual_arrival_dt"].dt.hour
    df["day_of_week"] = df["actual_arrival_dt"].dt.dayofweek
    df["is_weekend"] = df["day_of_week"].isin([5, 6])
    df["is_peak_hour"] = df["hour"].isin([7, 8, 9, 17, 18, 19])

    my_holidays = holidays.Malaysia(years=df["actual_arrival_dt"].dt.year.unique().tolist())
    df["is_public_holiday"] = df["actual_arrival_dt"].dt.date.astype(str).isin(
        [str(d) for d in my_holidays.keys()]
    )
    return df


def add_movement_features(df: pd.DataFrame, positions_clean: pd.DataFrame) -> pd.DataFrame:
    # bring in this vehicle's speed reading closest to the moment we're predicting for
    positions_sorted = positions_clean.sort_values("timestamp")
    df = df.sort_values("actual_arrival_ts")

    merged = pd.merge_asof(
        df, positions_sorted[["vehicle_id", "timestamp", "implied_speed_kmh"]],
        left_on="actual_arrival_ts", right_on="timestamp",
        by="vehicle_id", direction="backward"
    )
    merged = merged.rename(columns={"implied_speed_kmh": "current_speed_kmh"})
    merged["previous_speed_kmh"] = merged.groupby("vehicle_id")["current_speed_kmh"].shift(1)
    merged["acceleration"] = merged["current_speed_kmh"] - merged["previous_speed_kmh"]
    return merged


def add_historical_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("actual_arrival_dt")
    df["route_avg_delay_trailing"] = (
        df.groupby(["route_id", "hour"])["delay_minutes"]
        .transform(lambda x: x.shift(1).expanding().mean())
    )
    return df


def add_weather_features(df: pd.DataFrame, weather: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("actual_arrival_dt")
    weather = weather.sort_values("observed_at")

    merged = pd.merge_asof(
        df, weather,
        left_on="actual_arrival_dt", right_on="observed_at",
        direction="nearest", tolerance=pd.Timedelta("15min")
    )
    return merged


def check_missing_values(df: pd.DataFrame) -> pd.Series:
    missing = df.isna().sum()
    missing = missing[missing > 0]
    print(missing)
    return missing


def save_feature_table(df: pd.DataFrame, path: str) -> None:
    df.to_parquet(path, index=False)