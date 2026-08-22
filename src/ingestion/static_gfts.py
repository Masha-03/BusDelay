import requests
import zipfile
import pandas as pd


def download_static_gfts (category: str, dest_zip: str) -> None:
    response = requests.get("https://api.data.gov.my/gtfs-realtime/vehicle-position/prasarana",
                            params = {"category": category}
    )
    with open(dest_zip, "wb") as f:
        f.write(response.content)


def extract_gtfs_zip(zip_path: str, extract_to: str) -> None:
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(extract_to)


def load_routes(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def load_stops(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def load_trips(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def load_stop_times(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def load_shapes(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

