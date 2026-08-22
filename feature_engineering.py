import sys
sys.path.append("..")

import pandas as pd

from src.features.build_lables import match_arrival_to_stop, compute_delay
from src.features.build_features import (
    add_temporal_features, add_movement_features,
    add_historical_features, add_weather_features,
    check_missing_values, save_feature_table
)

# load your inputs first
positions_clean = pd.read_parquet("../data/processed/positions_clean.parquet")
stops = pd.read_csv("../data/raw/gtfs_static/rapid-bus-kl/stops.txt")
stop_times = pd.read_csv("../data/raw/gtfs_static/rapid-bus-kl/stop_times.txt")
weather = pd.read_csv("../data/raw/weather/weather_combined.csv")  # adjust to however you saved it

# now run the pipeline
matched = match_arrival_to_stop(positions_clean, stop_times, stops, radius_m=100)
labeled = compute_delay(matched)

featured = add_temporal_features(labeled)
featured = add_movement_features(featured, positions_clean)
featured = add_historical_features(featured)
featured = add_weather_features(featured, weather)

check_missing_values(featured)
save_feature_table(featured, "../data/processed/features.parquet")