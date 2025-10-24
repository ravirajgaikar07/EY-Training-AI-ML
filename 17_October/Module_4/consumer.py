import pika
import json
import time
import logging
import pandas as pd

logging.basicConfig(
    filename="consumer.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

visit_records = []


def process_and_save_report():
    if not visit_records:
        logger.warning("No visit records to process.")
        return
    df = pd.DataFrame(visit_records)
    df['Date'] = pd.to_datetime(df['Date'])
    avg_cost = df['Cost'].mean()
    most_visited_doc = df['DoctorID'].value_counts().idxmax()
    most_visited_count = df['DoctorID'].value_counts().max()
    visits_per_patient = df['PatientID'].value_counts()
    df['Month'] = df['Date'].dt.to_period('M')
    monthly_revenue = df.groupby('Month')['Cost'].sum()

    kpi_report = pd.DataFrame({
        "Metric": [
            "Average Cost Per Visit",
            "Most Visited Doctor",
            "Number of Visits Per Patient",
            "Monthly Revenue"
        ],
        "Value": [
            f"{avg_cost:.2f}",
            f"{most_visited_doc} ({most_visited_count} visits)",
            visits_per_patient.to_dict(),
            monthly_revenue.to_dict()
        ]
    })

    kpi_report.to_csv("kpi_report.csv", index=False)
    logger.info("KPI report saved to 'kpi_report.csv'")


def callback(ch, method, properties, body):
    start_time = time.time()
    try:
        visit = json.loads(body)
        visit['Cost'] = int(visit['Cost'])  # ensure Cost is int
        visit_records.append(visit)
        logger.info(f"Received visit: {visit}")
        process_and_save_report()
        ch.basic_ack(delivery_tag=method.delivery_tag)
        duration = time.time() - start_time
        logger.info(f"Processed visit in {duration:.4f} seconds")
    except Exception as e:
        logger.error(f"Error processing visit: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue='visit_tasks')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='visit_tasks', on_message_callback=callback)

    print("Waiting for visit messages. Press CTRL+C to exit.")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Consumer stopped.")


if __name__ == "__main__":
    main()
