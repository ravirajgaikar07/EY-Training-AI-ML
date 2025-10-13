import pandas as pd

#Extract
df=pd.read_csv("students.csv")

#Transform
df.dropna(inplace=True)
df["Marks"] = df["Marks"].astype(int)
df["Result"] = df["Marks"].apply(lambda x : "Pass" if x>=50 else "Fail")

#Load
df.to_csv("cleaned_students.csv", index=False)