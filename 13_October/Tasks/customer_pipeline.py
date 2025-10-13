import pandas as pd
from datetime import datetime

df=pd.read_csv("customers.csv")

df["AgeGroup"] = df["Age"].apply(lambda x: "Young" if x<30 else ("Adult" if 30<=x<50 else "Senior"))

df_younger = df[df["Age"] > 20]

df_younger.to_csv("filtered_customers.csv",index=False)
print(f"Time of execution : {datetime.now()}")