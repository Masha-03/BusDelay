# src/cleaning/clean_positions.py
import os
import glob
import logging
import pandas as pd
import pytz
from src.cleaning.geo_utils import implied_speed_kmh

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_raw_positions(raw_dir: str) -> pd.DataFrame:
    files = glob.glob(os.path.join(raw_dir, "*.csv"))
    dfs = [pd.read_csv(f) for f in files]
    combined = pd.concat(dfs, ignore_index=True)
    logger.info(f"Loaded {len(combined)} rows from {len(files)} files")
    return combined


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates()
    logger.info(f"Removed {before - len(df)} exact duplicate rows")
    return df


def filter_bounding_box(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    # Klang Valley approx bounding box
    mask = df["latitude"].between(2.9, 3.3) & df["longitude"].between(101.3, 101.8)
    df = df[mask]
    logger.info(f"Removed {before - len(df)} rows outside the bounding box")
    return df


def add_speed_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["vehicle_id", "timestamp"])
    df["prev_lat"] = df.groupby("vehicle_id")["latitude"].shift(1)
    df["prev_lon"] = df.groupby("vehicle_id")["longitude"].shift(1)
    df["prev_timestamp"] = df.groupby("vehicle_id")["timestamp"].shift(1)
    df["seconds_elapsed"] = df["timestamp"] - df["prev_timestamp"]

    df["implied_speed_kmh"] = df.apply(
        lambda row: implied_speed_kmh(
            row["prev_lat"], row["prev_lon"],
            row["latitude"], row["longitude"],
            row["seconds_elapsed"]
        ) if pd.notna(row["prev_lat"]) else 0.0,
        axis=1
    )
    return df


def flag_impossible_speed(df: pd.DataFrame, max_kmh: float = 120) -> pd.DataFrame:
    before = len(df)
    df = df[df["implied_speed_kmh"] <= max_kmh]
    logger.info(f"Removed {before - len(df)} rows with implied speed above {max_kmh} km/h")
    return df


def flag_stationary_vehicles(df: pd.DataFrame, minutes: int = 10) -> pd.DataFrame:
    threshold_seconds = minutes * 60
    df["is_stationary"] = (
        (df["implied_speed_kmh"] == 0) & (df["seconds_elapsed"] >= threshold_seconds)
    )
    logger.info(f"Flagged {df['is_stationary'].sum()} rows as stationary")
    return df


def convert_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    kl_tz = pytz.timezone("Asia/Kuala_Lumpur")
    df["observed_at"] = pd.to_datetime(df["timestamp"], unit="s", utc=True).dt.tz_convert(kl_tz)
    return df


def validate_route_ids(df: pd.DataFrame, static_routes: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    valid_ids = set(static_routes["route_id"])
    df = df[df["route_id"].isin(valid_ids)]
    logger.info(f"Removed {before - len(df)} rows with unmatched route_id")
    return df


def clean_vehicle_positions(raw_dir: str, static_routes: pd.DataFrame) -> pd.DataFrame:
    df = load_raw_positions(raw_dir)
    df = remove_duplicates(df)
    df = filter_bounding_box(df)
    df = add_speed_columns(df)
    df = flag_impossible_speed(df)
    df = flag_stationary_vehicles(df)
    df = convert_timestamps(df)
    df = validate_route_ids(df, static_routes)
    logger.info(f"Final clean dataset: {len(df)} rows")
    return df