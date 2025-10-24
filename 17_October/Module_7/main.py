import pandas as pd
from datetime import datetime

# Step 1: Extract
visits = pd.read_csv("visits.csv")

# Step 2: Transform
visits["Date"] = pd.to_datetime(visits["Date"])
visits["DayOfWeek"] = visits["Date"].dt.day_name()
# Step 3: Load
today_str = datetime.today().strftime("%Y%m%d")
filename = f"daily_visits_report_{today_str}.csv"
visits.to_csv(filename, index=False)

print(f"ETL complete. Report saved as {filename}")