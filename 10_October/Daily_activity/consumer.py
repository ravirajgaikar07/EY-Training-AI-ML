# consumer.py
import pika
import json
import time

# 1. Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()

# 2. Ensure the queue exists
channel.queue_declare(queue="student_tasks")

# 3. Define message handling function
def callback(ch, method, properties, body):
    task = json.loads(body)
    print("Received:", task)
    # Simulate some work
    time.sleep(2)
    print("Task processed for student:", task["student_id"])

# 4. Start consuming messages from the queue
channel.basic_consume(queue="student_tasks", on_message_callback=callback, auto_ack=True)

print("Waiting for messages. Press CTRL+C to exit.")
channel.start_consuming()