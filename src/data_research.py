import pandas as pd
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

def run_research():
    processed_dir = Path("data/processed")
    print("\n--- АНАЛІТИЧНЕ ДОСЛІДЖЕННЯ ПОКАЗНИКІВ ЗАРПЛАТИ ---")

    # --- ГІПОТЕЗИ 1 та 2 (Галузеві дані) ---
    df_ind = pd.read_csv(processed_dir / "2_wage_by_industry.csv")
    
    # 1. Очищення всіх потенційних числових колонок від пробілів та ком
    for col in ['ЗП_жовтень_2019', 'Темп_росту_ЗП_відсотки', 'Індекс_росту_цін']:
        df_ind[col] = df_ind[col].astype(str).str.replace(r'\s+', '', regex=True).str.replace(',', '.')
        df_ind[col] = pd.to_numeric(df_ind[col], errors='coerce')

    # 2. Виправлення зміщення колонок Excel (Smart Coalesce)
    # Якщо бачимо NaN у ЗП, забираємо число з Темпу росту. Темп росту беремо з Індексу.
    df_ind['Дійсна_ЗП'] = df_ind['ЗП_жовтень_2019'].fillna(df_ind['Темп_росту_ЗП_відсотки'])
    df_ind['Дійсний_Темп'] = df_ind.apply(
        lambda row: row['Індекс_росту_цін'] if pd.isna(row['ЗП_жовтень_2019']) else row['Темп_росту_ЗП_відсотки'],
        axis=1
    )

    # 3. Фільтрація підсумкового рядка за новою колонкою
    df_ind_clean = df_ind[~df_ind['Вид_діяльності'].str.contains('УСЬОГО', na=False)].dropna(subset=['Дійсна_ЗП'])
    
    # Гіпотеза 1
    top_growth = df_ind_clean.loc[df_ind_clean['Дійсний_Темп'].idxmax()]
    print("\n1. Результати перевірки гіпотези приросту:")
    print(f"   - Галузь-лідер: {top_growth['Вид_діяльності']}")
    print(f"   - Показник темпу росту: {top_growth['Дійсний_Темп']}%")

    # Гіпотеза 2
    production_categories = ['Промисловість', 'Будівництво', 'Сільське', 'Транспорт']
    
    def define_sector(activity):
        for category in production_categories:
            if category in str(activity):
                return 'Виробничий сектор'
        return 'Сфера послуг'
    
    df_ind_clean['Сектор'] = df_ind_clean['Вид_діяльності'].apply(define_sector)
    sector_analysis = df_ind_clean.groupby('Сектор')['Дійсна_ЗП'].mean().round(2)
    
    print("\n2. Порівняння оплати праці за секторами:")
    print(f"   - Середня ЗП у виробничому секторі: {sector_analysis.get('Виробничий сектор', 0)} грн")
    print(f"   - Середня ЗП у сфері послуг: {sector_analysis.get('Сфера послуг', 0)} грн")

    # --- ГІПОТЕЗА 3 (Регіональні дані) ---
    df_reg = pd.read_csv(processed_dir / "3_wage_by_region.csv")
    
    # Очищення числових даних
    df_reg['Заробітна_плата_грн'] = df_reg['Заробітна_плата_грн'].astype(str).str.replace(r'\s+', '', regex=True).str.replace(',', '.')
    df_reg['Заробітна_плата_грн'] = pd.to_numeric(df_reg['Заробітна_плата_грн'], errors='coerce')
    
    df_reg_clean = df_reg[~df_reg['Регіон'].str.contains('Україна', na=False)].dropna(subset=['Заробітна_плата_грн'])
    
    max_wage_reg = df_reg_clean.loc[df_reg_clean['Заробітна_плата_грн'].idxmax()]
    min_wage_reg = df_reg_clean.loc[df_reg_clean['Заробітна_плата_грн'].idxmin()]
    
    print("\n3. Регіональний аналіз:")
    print(f"   - Регіон з найвищою ЗП: {max_wage_reg['Регіон']} ({max_wage_reg['Заробітна_плата_грн']} грн)")
    print(f"   - Регіон з найнижчою ЗП: {min_wage_reg['Регіон']} ({min_wage_reg['Заробітна_плата_грн']} грн)")
    print("\n" + "-"*50)

if __name__ == "__main__":
    run_research()