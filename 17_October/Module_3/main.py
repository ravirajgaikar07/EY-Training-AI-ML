import pandas as pd

patients = pd.read_csv("patients.csv")
doctors = pd.read_csv("doctors.csv")
visits = pd.read_csv("visits.csv")

df = pd.merge(visits, patients, on="PatientID", how="inner")
df = pd.merge(df, doctors, on="DoctorID", how="inner")

df["Date"] = pd.to_datetime(df["Date"])
df["Month"] = df["Date"].dt.month_name()

visit_counts = df["PatientID"].value_counts()
df["FollowUpRequired"] = df["PatientID"].apply(lambda x: "Yes" if visit_counts[x] > 1 else "No")

df.to_csv("processed_visits.csv", index=False)