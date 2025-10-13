import pandas as pd
from datetime import datetime

def run_pipeline():
    df = pd.read_csv('sales.csv')
    df['Total'] = df['Quantity'] * df['Price']
    df.to_csv("daily_report.csv", index=False)
    print(f"Pipeline completed at {datetime.now()}")

if __name__=="__main__":
    run_pipeline()