import json
import time
import queue
import threading
import logging
import pandas as pd

report = []
visit_queue = queue.Queue()

patients = pd.read_csv("patients.csv")
doctors = pd.read_csv("doctors.csv")
visits = pd.read_csv("visits.csv")

def producer():
    for _, row in visits.iterrows():
        visit_json = json.dumps(row.to_dict())
        visit_queue.put(visit_json)
        print(f"Produced: {visit_json}")

logging.basicConfig(filename='visit_processing.log', level=logging.INFO)

def consumer():
    global report
    while not visit_queue.empty():
        visit_json = visit_queue.get()
        start_time = time.time()
        try:
            visit = json.loads(visit_json)
            patient = patients[patients["PatientID"] == visit["PatientID"]].iloc[0].to_dict()
            doctor = doctors[doctors["DoctorID"] == visit["DoctorID"]].iloc[0].to_dict()

            enriched = {
                "VisitID": visit["VisitID"],
                "Date": visit["Date"],
                "Cost": visit["Cost"],
                "PatientName": patient["Name"],
                "Age": patient["Age"],
                "Gender": patient["Gender"],
                "Condition": patient["Condition"],
                "DoctorName": doctor["Name"],
                "Specialization": doctor["Specialization"]
            }

            report.append(enriched)
            logging.info(f"{visit['VisitID']} processed successfully in {time.time() - start_time:.2f}s")
        except Exception as e:
            logging.error(f"{visit['VisitID']} failed: {str(e)}")

def save_report(report):
    df = pd.DataFrame(report)
    df.to_csv("visit_report.csv", index=False)
    print("Report saved as visit_report.csv")

producer_thread = threading.Thread(target=producer)
consumer_thread = threading.Thread(target=consumer)

producer_thread.start()
consumer_thread.start()

producer_thread.join()
consumer_thread.join()

save_report(report)