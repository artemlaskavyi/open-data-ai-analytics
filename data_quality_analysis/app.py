import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
import os
import time

def analyze_data_quality():
    report_path = Path("/app/reports/data_quality_report.md")
    report_path.parent.mkdir(exist_ok=True, parents=True)

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set")

    engine = create_engine(db_url)
    
    # Wait for DB and tables to be ready
    for _ in range(15):
        try:
            with engine.connect() as conn:
                # check if tables exist
                pd.read_sql("SELECT 1 FROM wage_by_region LIMIT 1", conn)
                break
        except Exception as e:
            print("Waiting for database tables to be ready...")
            time.sleep(5)
    else:
        raise Exception("Database tables are not ready.")

    report = ["# Звіт про якість даних\n"]

    # 1. Перевірка регіональних даних
    df_regions = pd.read_sql("SELECT * FROM wage_by_region", engine)
    report.append("## 1. Аналіз регіональних даних")
    
    missing_total = df_regions.isnull().sum().sum()
    missing_min_wage = df_regions['Мінімальна_ЗП'].isnull().sum()
    
    report.append(f"- Загальна кількість пропусків: {missing_total}")
    
    # Виявлення структурної аномалії
    if missing_min_wage > 0:
        report.append(f"- [АНОМАЛІЯ]: Виявлено {missing_min_wage} пропусків у колонці 'Мінімальна_ЗП' (особливість Excel).")
        
    if df_regions['Заробітна_плата_грн'].min() <= 0:
        report.append("- [ПОМИЛКА]: Знайдено нульові або від'ємні значення середніх зарплат.")
    else:
        report.append("- Базові значення середніх зарплат коректні (всі > 0).")

    invalid_ratio = df_regions[df_regions['Співвідношення_відсотки'] < 100]
    if not invalid_ratio.empty:
        report.append("- [УВАГА]: Є регіони, де середня зарплата менша за мінімальну.")
    else:
        report.append("- В усіх регіонах середня зарплата перевищує мінімальну.")

    # 2. Перевірка галузевих даних
    df_industry = pd.read_sql("SELECT * FROM wage_by_industry", engine)
    report.append("\n## 2. Аналіз галузевих даних")
    report.append(f"- Кількість унікальних галузей: {df_industry['Вид_діяльності'].nunique()}")
    duplicates = df_industry.duplicated().sum()
    report.append(f"- Повних дублікатів рядків: {duplicates}")

    # Збереження звіту
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    print(f"Детальний звіт про якість збережено у {report_path}")

if __name__ == "__main__":
    analyze_data_quality()
