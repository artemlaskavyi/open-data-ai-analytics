import pandas as pd
from pathlib import Path

def preprocess_excel(input_path: Path, output_dir: Path):
    if not input_path.exists():
        print(f"❌ Файл не знайдено: {input_path}")
        return
        
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"🔄 Починаємо обробку файлу: {input_path.name}...")

    # 1. Номінальна заробітна плата (Колонки A-D)
    df_nominal = pd.read_excel(
        input_path, 
        header=56, 
        nrows=12, 
        usecols="A:D" 
    )
    df_nominal.columns = ["Період", "2018_рік", "2019_рік", "Відсотки_до_2018"]
    df_nominal.to_csv(output_dir / "1_nominal_wage.csv", index=False)
    print("✅ Таблиця 1 (Номінальна ЗП) збережена.")

    # 2. Стан забезпечення випереджаючого зростання (Колонки A-E)
    col_names_2 = [
        "Вид_діяльності", 
        "ЗП_жовтень_2019", 
        "Темп_росту_ЗП_відсотки", 
        "Індекс_росту_цін", 
        "Співвідношення_темпів"
    ]
    df_industry = pd.read_excel(
        input_path, 
        skiprows=83, 
        nrows=19, 
        usecols="A:E",
        names=col_names_2
    )
    df_industry.to_csv(output_dir / "2_wage_by_industry.csv", index=False)
    print("✅ Таблиця 2 (За видами економічної діяльності) збережена.")

    # 3. Співвідношення ЗП по регіонах (Колонки A, C, D, E - пропускаємо порожню B)
    df_regions = pd.read_excel(
        input_path, 
        header=184, 
        nrows=26, 
        usecols="A,C:E" 
    )
    df_regions.columns = ["Регіон", "Мінімальна_ЗП", "Заробітна_плата_грн", "Співвідношення_відсотки"]
    df_regions.to_csv(output_dir / "3_wage_by_region.csv", index=False)
    print("✅ Таблиця 3 (По регіонах) збережена.")

    # 4. Реальна заробітна плата (Колонки A-E)
    df_real = pd.read_excel(
        input_path, 
        header=231, 
        nrows=12, 
        usecols="A:E"
    )
    df_real.columns = ["Період", "2016_рік", "2017_рік", "2018_рік", "2019_рік"]
    df_real.to_csv(output_dir / "4_real_wage.csv", index=False)
    print("✅ Таблиця 4 (Реальна ЗП) збережена.")

    print(f"🎉 Всі дані успішно оброблено та збережено в {output_dir}")

if __name__ == "__main__":
    RAW_FILE = Path("data/raw/monzp102019.xlsx")
    PROCESSED_DIR = Path("data/processed")
    preprocess_excel(RAW_FILE, PROCESSED_DIR)