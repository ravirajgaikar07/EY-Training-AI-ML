from fastapi import FastAPI
import asyncio
import time

app=FastAPI()

@app.get("/sync-tasks")
def sync_task():
    time.sleep(10)
    return{"message": "Sync task completed after 10 seconds"}

@app.get("/async-tasks")
async def async_task():
    await asyncio.sleep(10)
    return{"message": "Async task completed after 10 seconds"}