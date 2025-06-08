# result-api/app/main.py
import json
import logging
import threading
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
import time

logging.basicConfig(level=logging.INFO)
app = FastAPI()

results_db = {}


origins = ["http://localhost:8080"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def kafka_consumer_thread():
    config = load_config()
    kafka_config = config.get("kafka", {})
    
    consumer = None
    retries = 5
    delay = 5
    for i in range(retries):
        try:
            consumer = KafkaConsumer(
                kafka_config["result_topic"],
                bootstrap_servers=kafka_config["bootstrap_servers"],
                auto_offset_reset='earliest',
                group_id=kafka_config["consumer_group_id"],
                value_deserializer=lambda v: json.loads(v.decode('utf-8'))
            )
            logging.info("Kafka Consumer for Result API connected successfully.")
            break
        except NoBrokersAvailable:
            logging.warning(f"Kafka not available for Result API, retrying in {delay}s...")
            time.sleep(delay)

    if not consumer:
        logging.error("Could not connect Result API to Kafka. Thread exiting.")
        return

    logging.info("Result API consumer thread started and waiting for messages...")
    for message in consumer:
        result = message.value
        domain = result.get("domain")
        if domain:
            logging.info(f"Result received and stored for domain: {domain}")
            results_db[domain] = result

# --- Endpoints de la API ---
@app.get("/results/{domain}")
async def get_result(domain: str):
    if domain in results_db:
        return results_db[domain]
    else:
        raise HTTPException(status_code=404, detail="Result not found. The scan may still be in progress or failed.")

@app.on_event("startup")
async def startup_event():
    thread = threading.Thread(target=kafka_consumer_thread, daemon=True)
    thread.start()