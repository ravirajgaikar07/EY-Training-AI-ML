import pandas as pd

visits = pd.read_csv('visits.csv')

visits["Date"] = pd.to_datetime(visits["Date"])

# Average cost per visit
avg_cost = visits["Cost"].mean()

# Most visited doctor
most_visited_doctor = visits["DoctorID"].value_counts().idxmax()

# Number of visits per patient
visits_per_patient = visits.groupby("PatientID").size().reset_index(name="VisitCount")

# Monthly revenue
visits["Month"] = visits["Date"].dt.to_period("M")
monthly_revenue = visits.groupby("Month")["Cost"].sum().reset_index()
monthly_revenue.columns = ["Month", "Revenue"]

# Save KPI report
kpi_summary = pd.DataFrame({
    "Metric": ["Average Cost per Visit", "Most Visited Doctor"],
    "Value": [avg_cost, most_visited_doctor]
})

# Save to CSV
kpi_summary.to_csv("kpi_report.csv", index=False)
visits_per_patient.to_csv("visits_per_patient.csv", index=False)
monthly_revenue.to_csv("monthly_revenue.csv", index=False)

print("KPI report saved as kpi_report.csv")