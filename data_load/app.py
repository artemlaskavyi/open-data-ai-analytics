import requests
import pandas as pd
from pathlib import Path
import sys
import os
from sqlalchemy import create_engine
import time

DATA_URL = "https://data.gov.ua/dataset/aa28bd6b-c8c5-418c-9a1f-d65a519f4555/resource/6980f479-f4e7-4089-aaf7-7ac72d53dec6/download/monzp102019.xlsx"
DATA_DIR = Path("/app/data/raw")
FILE_PATH = DATA_DIR / "monzp102019.xlsx"

def download_dataset(url: str, path: Path):
    print(f"Downloading dataset from {url} ...")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(response.content)
    print(f"Dataset successfully saved to {path}")

def process_and_load_to_db(input_path: Path):
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    print(f"🔄 Processing file: {input_path.name}...")
    
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set")

    engine = create_engine(db_url)
    
    # Wait for DB to be ready
    for i in range(10):
        try:
            with engine.connect() as conn:
                print("Database connection successful.")
                break
        except Exception as e:
            print(f"Failed to connect to database. Retrying in 5s... ({e})")
            time.sleep(5)
    else:
        raise ConnectionError("Could not connect to the database after several retries.")

    # 1. Nominal Wage
    df_nominal = pd.read_excel(input_path, header=56, nrows=12, usecols="A:D")
    df_nominal.columns = ["Період", "2018_рік", "2019_рік", "Відсотки_до_2018"]
    df_nominal.to_sql("nominal_wage", engine, if_exists="replace", index=False)
    print("✅ Table 1 (nominal_wage) loaded to DB.")

    # 2. Wage by Industry
    col_names_2 = ["Вид_діяльності", "ЗП_жовтень_2019", "Темп_росту_ЗП_відсотки", "Індекс_росту_цін", "Співвідношення_темпів"]
    df_industry = pd.read_excel(input_path, skiprows=83, nrows=19, usecols="A:E", names=col_names_2)
    df_industry.to_sql("wage_by_industry", engine, if_exists="replace", index=False)
    print("✅ Table 2 (wage_by_industry) loaded to DB.")


    # 3. Wage by Region
    df_regions = pd.read_excel(input_path, header=184, nrows=26, usecols="A,C:E")
    df_regions.columns = ["Регіон", "Мінімальна_ЗП", "Заробітна_плата_грн", "Співвідношення_відсотки"]
    df_regions.to_sql("wage_by_region", engine, if_exists="replace", index=False)
    print("✅ Table 3 (wage_by_region) loaded to DB.")

    # 4. Real Wage
    df_real = pd.read_excel(input_path, header=231, nrows=12, usecols="A:E")
    df_real.columns = ["Період", "2016_рік", "2017_рік", "2018_рік", "2019_рік"]
    df_real.to_sql("real_wage", engine, if_exists="replace", index=False)
    print("✅ Table 4 (real_wage) loaded to DB.")

    print("🎉 All data successfully processed and loaded to DB!")

if __name__ == "__main__":
    try:
        download_dataset(DATA_URL, FILE_PATH)
        process_and_load_to_db(FILE_PATH)
    except Exception as e:
        print(f"Data load failed: {e}")
        sys.exit(1)
