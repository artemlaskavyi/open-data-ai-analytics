import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sqlalchemy import create_engine
import os
import time

def create_visualizations():
    figures_dir = Path("/app/plots")
    figures_dir.mkdir(parents=True, exist_ok=True)

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set")

    engine = create_engine(db_url)
    
    # Wait for DB and tables to be ready
    for _ in range(15):
        try:
            with engine.connect() as conn:
                pd.read_sql("SELECT 1 FROM wage_by_region LIMIT 1", conn)
                break
        except Exception as e:
            print("Waiting for database tables to be ready...")
            time.sleep(5)
    else:
        raise Exception("Database tables are not ready.")

    # Завантаження даних по регіонах
    df_reg = pd.read_sql("SELECT * FROM wage_by_region", engine)
    df_reg['Заробітна_плата_грн'] = df_reg['Заробітна_плата_грн'].astype(str).str.replace(r'\s+', '', regex=True).str.replace(',', '.')
    df_reg['Заробітна_плата_грн'] = pd.to_numeric(df_reg['Заробітна_плата_грн'], errors='coerce')
    
    df_reg = df_reg[~df_reg['Регіон'].str.contains('Україна', na=False)].dropna(subset=['Заробітна_плата_грн']).sort_values('Заробітна_плата_грн', ascending=True)

    # Побудова графіка
    plt.figure(figsize=(10, 8))
    plt.barh(df_reg['Регіон'], df_reg['Заробітна_плата_грн'], color='skyblue')
    plt.title('Середня заробітна плата за регіонами (жовтень 2019)')
    plt.xlabel('Гривні')
    plt.tight_layout()

    # Збереження
    plot_path = figures_dir / "regional_wages.png"
    plt.savefig(plot_path)
    print(f"Графік збережено у {plot_path}")
    plt.close()

    # Завантаження даних по галузях
    df_ind = pd.read_sql("SELECT * FROM wage_by_industry", engine)
    for col in ['ЗП_жовтень_2019', 'Темп_росту_ЗП_відсотки']:
        df_ind[col] = df_ind[col].astype(str).str.replace(r'\s+', '', regex=True).str.replace(',', '.')
        df_ind[col] = pd.to_numeric(df_ind[col], errors='coerce')
    df_ind['Дійсна_ЗП'] = df_ind['ЗП_жовтень_2019'].fillna(df_ind['Темп_росту_ЗП_відсотки'])
    df_ind = df_ind[~df_ind['Вид_діяльності'].str.contains('УСЬОГО', na=False)].dropna(subset=['Дійсна_ЗП'])
    top_ind = df_ind.sort_values('Дійсна_ЗП', ascending=False).head(10).sort_values('Дійсна_ЗП', ascending=True)

    plt.figure(figsize=(10, 6))
    plt.barh(top_ind['Вид_діяльності'], top_ind['Дійсна_ЗП'], color='coral')
    plt.title('Топ-10 галузей з найвищою зарплатою (жовтень 2019)')
    plt.xlabel('Гривні')
    plt.yticks(fontsize=8)
    plt.tight_layout()
    industry_plot_path = figures_dir / "industry_wages.png"
    plt.savefig(industry_plot_path)
    print(f"Графік збережено у {industry_plot_path}")
    plt.close()

if __name__ == "__main__":
    create_visualizations()
