# app/main.py
import json
import logging
import time
from kafka import KafkaConsumer
from .base_service import BaseMicroservice

logging.basicConfig(level=logging.INFO)

class ResultHandlerService(BaseMicroservice):
    def __init__(self, config_path: str):
        super().__init__(config_path)
        self.consumer = self._setup_kafka_consumer()

    def _setup_kafka_consumer(self):
        try:
            consumer = KafkaConsumer(
                self.kafka_config["result_topic"],
                bootstrap_servers=self.kafka_config["bootstrap_servers"],
                auto_offset_reset='earliest',
                group_id=self.kafka_config["consumer_group_id"],
                value_deserializer=lambda v: json.loads(v.decode('utf-8'))
            )
            logging.info("Kafka Consumer for Result Handler connected successfully.")
            return consumer
        except Exception as e:
            logging.error(f"Failed to connect Kafka Consumer: {e}")
            return None

    def run(self):
        if not self.consumer:
            logging.error("Service cannot run without Kafka connection. Exiting.")
            return
            
        logging.info(f"{self.service_name} is running and waiting for results...")
        for message in self.consumer:
            result = message.value
            logging.info("--- SCAN RESULT RECEIVED ---")
            print(json.dumps(result, indent=2))
            logging.info("--------------------------")

if __name__ == "__main__":
    time.sleep(20)
    service = ResultHandlerService(config_path="../config.json")
    service.run()