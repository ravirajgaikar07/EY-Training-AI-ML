import threading
import queue
import time
import json

task_queue = queue.Queue()

# Producer thread function
def producer():
    tasks = [
        {"student_id": 101, "action": "generate_certificate", "email": "rahul@example.com"},
        {"student_id": 102, "action": "send_reminder", "email": "sara@example.com"},
        {"student_id": 103, "action": "update_profile", "email": "alex@example.com"},
    ]
    for task in tasks:
        task_json = json.dumps(task)
        print("[Producer] Adding task:", task)
        task_queue.put(task_json)
        time.sleep(1)

    task_queue.put(None)
    print("[Producer] No more tasks. Sent stop signal.")

# Consumer thread function
def consumer():
    while True:
        task_json = task_queue.get()
        if task_json is None:
            print("[Consumer] Stop signal received. Exiting.")
            task_queue.task_done()
            break
        task = json.loads(task_json)
        print("[Consumer] Processing task for student:", task["student_id"])
        time.sleep(2)
        print("[Consumer] Done processing:", task["student_id"])
        task_queue.task_done()

# Create threads
producer_thread = threading.Thread(target=producer)
consumer_thread = threading.Thread(target=consumer)

# Start threads
consumer_thread.start()
producer_thread.start()

producer_thread.join()

task_queue.join()

print("All tasks have been processed.")
