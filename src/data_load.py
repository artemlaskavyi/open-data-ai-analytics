import requests
from pathlib import Path

DATA_URL = "https://data.gov.ua/dataset/aa28bd6b-c8c5-418c-9a1f-d65a519f4555/resource/6980f479-f4e7-4089-aaf7-7ac72d53dec6/download/monzp102019.xlsx"
DATA_DIR = Path("data/raw")
DATA_DIR.mkdir(parents=True, exist_ok=True)
FILE_PATH = DATA_DIR / "monzp102019.xlsx"

def download_dataset(url: str, path: Path):
    try:
        print(f"Downloading dataset from {url} ...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(path, "wb") as f:
            f.write(response.content)
        print(f"Dataset successfully saved to {path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading data: {e}")

if __name__ == "__main__":
    download_dataset(DATA_URL, FILE_PATH)