from flask import Flask, render_template, send_from_directory
from pathlib import Path
import markdown
import json
import os
import pandas as pd
from sqlalchemy import create_engine

app = Flask(__name__)

REPORTS_DIR = Path("/app/reports")
PLOTS_DIR = Path("/app/plots")

def get_db_data():
    try:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            return None
        engine = create_engine(db_url)
        with engine.connect() as conn:
            df = pd.read_sql("SELECT * FROM real_wage LIMIT 10", conn)
            if '2016_рік' in df.columns:
                df = df.drop(columns=['2016_рік'])
            return df.to_html(classes="data-table", index=False)
    except Exception as e:
        print(f"Error fetching DB data: {e}")
        return None

@app.route('/')
def index():
    # Read data quality report
    dq_md = ""
    dq_path = REPORTS_DIR / "data_quality_report.md"
    if dq_path.exists():
        with open(dq_path, "r", encoding="utf-8") as f:
            dq_md = f.read()
    dq_html = markdown.markdown(dq_md)

    # Read research report
    research_data = {}
    r_path = REPORTS_DIR / "research_report.json"
    if r_path.exists():
        with open(r_path, "r", encoding="utf-8") as f:
            research_data = json.load(f)

    db_table_html = get_db_data()

    return render_template(
        'index.html', 
        dq_html=dq_html, 
        research_data=research_data,
        db_table=db_table_html
    )

@app.route('/plots/<path:filename>')
def serve_plot(filename):
    return send_from_directory(PLOTS_DIR, filename)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
