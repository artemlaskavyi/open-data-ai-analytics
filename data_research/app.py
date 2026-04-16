import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
import warnings
import json
import os
import time

warnings.filterwarnings('ignore')

def run_research():
    report_path = Path("/app/reports/research_report.json")
    report_path.parent.mkdir(exist_ok=True, parents=True)

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set")

    engine = create_engine(db_url)
    
    # Wait for DB and tables to be ready
    for _ in range(15):
        try:
            with engine.connect() as conn:
                pd.read_sql("SELECT 1 FROM wage_by_industry LIMIT 1", conn)
                break
        except Exception as e:
            print("Waiting for database tables to be ready...")
            time.sleep(5)
    else:
        raise Exception("Database tables are not ready.")

    print("\n--- АНАЛІТИЧНЕ ДОСЛІДЖЕННЯ ПОКАЗНИКІВ ЗАРПЛАТИ ---")
    results = {}

    # --- ГІПОТЕЗИ 1 та 2 (Галузеві дані) ---
    df_ind = pd.read_sql("SELECT * FROM wage_by_industry", engine)
    
    # Очищення всіх потенційних числових колонок від пробілів та ком
    for col in ['ЗП_жовтень_2019', 'Темп_росту_ЗП_відсотки', 'Індекс_росту_цін']:
        df_ind[col] = df_ind[col].astype(str).str.replace(r'\s+', '', regex=True).str.replace(',', '.')
        df_ind[col] = pd.to_numeric(df_ind[col], errors='coerce')

    # Виправлення зміщення колонок Excel
    df_ind['Дійсна_ЗП'] = df_ind['ЗП_жовтень_2019'].fillna(df_ind['Темп_росту_ЗП_відсотки'])
    df_ind['Дійсний_Темп'] = df_ind.apply(
        lambda row: row['Індекс_росту_цін'] if pd.isna(row['ЗП_жовтень_2019']) else row['Темп_росту_ЗП_відсотки'],
        axis=1
    )

    df_ind_clean = df_ind[~df_ind['Вид_діяльності'].str.contains('УСЬОГО', na=False)].dropna(subset=['Дійсна_ЗП'])
    
    # Гіпотеза 1
    top_growth = df_ind_clean.loc[df_ind_clean['Дійсний_Темп'].idxmax()]
    results["hypothesis_1"] = {
        "leader_industry": str(top_growth['Вид_діяльності']),
        "growth_rate_percent": float(top_growth['Дійсний_Темп'])
    }

    # Гіпотеза 2
    production_categories = ['Промисловість', 'Будівництво', 'Сільське', 'Транспорт']
    def define_sector(activity):
        for category in production_categories:
            if category in str(activity):
                return 'Виробничий сектор'
        return 'Сфера послуг'
    
    df_ind_clean['Сектор'] = df_ind_clean['Вид_діяльності'].apply(define_sector)
    sector_analysis = df_ind_clean.groupby('Сектор')['Дійсна_ЗП'].mean().round(2)
    
    results["hypothesis_2"] = {
        "production_sector_avg_wage": float(sector_analysis.get('Виробничий сектор', 0)),
        "service_sector_avg_wage": float(sector_analysis.get('Сфера послуг', 0))
    }

    # --- ГІПОТЕЗА 3 (Регіональні дані) ---
    df_reg = pd.read_sql("SELECT * FROM wage_by_region", engine)
    
    # Очищення числових даних
    df_reg['Заробітна_плата_грн'] = df_reg['Заробітна_плата_грн'].astype(str).str.replace(r'\s+', '', regex=True).str.replace(',', '.')
    df_reg['Заробітна_плата_грн'] = pd.to_numeric(df_reg['Заробітна_плата_грн'], errors='coerce')
    
    df_reg_clean = df_reg[~df_reg['Регіон'].str.contains('Україна', na=False)].dropna(subset=['Заробітна_плата_грн'])
    
    max_wage_reg = df_reg_clean.loc[df_reg_clean['Заробітна_плата_грн'].idxmax()]
    min_wage_reg = df_reg_clean.loc[df_reg_clean['Заробітна_плата_грн'].idxmin()]
    
    results["hypothesis_3"] = {
        "max_wage_region": str(max_wage_reg['Регіон']),
        "max_wage": float(max_wage_reg['Заробітна_плата_грн']),
        "min_wage_region": str(min_wage_reg['Регіон']),
        "min_wage": float(min_wage_reg['Заробітна_плата_грн']),
        "mean_wage_all_regions": float(df_reg_clean['Заробітна_плата_грн'].mean())
    }

    # Найдетальніша аналітика по галузях
    top_3_ind = df_ind_clean.sort_values(by='Дійсна_ЗП', ascending=False).head(3)
    results["detailed_analysis"] = {
        "top_3_industries_by_wage": [
            {"industry": str(row['Вид_діяльності']), "wage": float(row['Дійсна_ЗП'])}
            for _, row in top_3_ind.iterrows()
        ]
    }

    # Збереження
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print(f"Звіт дослідження збережено у {report_path}")

if __name__ == "__main__":
    run_research()
