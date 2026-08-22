from src.ingestion.ingestion.realtime_gtfs import fetch_raw_feed, decode_feed, feed_to_dataframe, save_snapshot

raw = fetch_raw_feed("rapid-bus-kl")
feed = decode_feed(raw)
df = feed_to_dataframe(feed)
save_snapshot(df, "data/raw/positions/")

print(df.head())