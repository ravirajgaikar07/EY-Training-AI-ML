import pika
import json
import pandas as pd

visits = pd.read_csv("visits.csv")

connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
channel.queue_declare(queue="visit_tasks")

for _, row in visits.iterrows():
    message = row.to_dict()
    channel.basic_publish(
        exchange='',
        routing_key='visit_tasks',
        body=json.dumps(message)
    )
    print(f"Sent visit: {message}")

connection.close()
