import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def create_visualizations():
    processed_dir = Path("data/processed")
    figures_dir = Path("reports/figures")
    figures_dir.mkdir(parents=True, exist_ok=True)

    # Завантаження даних по регіонах
    df_reg = pd.read_csv(processed_dir / "3_wage_by_region.csv")
    df_reg = df_reg[~df_reg['Регіон'].str.contains('Україна', na=False)].sort_values('Заробітна_плата_грн', ascending=True)

    # Побудова графіка
    plt.figure(figsize=(10, 8))
    plt.barh(df_reg['Регіон'], df_reg['Заробітна_плата_грн'], color='skyblue')
    plt.title('Середня заробітна плата за регіонами (жовтень 2019)')
    plt.xlabel('Гривні')
    plt.tight_layout()

    # Збереження
    plt.savefig(figures_dir / "regional_wages.png")
    print(f"Графік збережено у {figures_dir / 'regional_wages.png'}")

if __name__ == "__main__":
    create_visualizations()