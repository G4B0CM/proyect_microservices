# app/main.py
import json
import logging
import time
import dns.resolver
import whois
from kafka import KafkaConsumer, KafkaProducer
from .base_service import BaseMicroservice

logging.basicConfig(level=logging.INFO)

class ScannerService(BaseMicroservice):
    def __init__(self, config_path: str):
        super().__init__(config_path)
        self.consumer = self._setup_kafka_consumer()
        self.producer = self._setup_kafka_producer()
    
    def _setup_kafka_consumer(self):
        try:
            consumer = KafkaConsumer(
                self.kafka_config["request_topic"],
                bootstrap_servers=self.kafka_config["bootstrap_servers"],
                auto_offset_reset='earliest',
                group_id=self.kafka_config["consumer_group_id"],
                value_deserializer=lambda v: json.loads(v.decode('utf-8'))
            )
            logging.info("Kafka Consumer for Scanner connected successfully.")
            return consumer
        except Exception as e:
            logging.error(f"Failed to connect Kafka Consumer: {e}")
            return None

    def _setup_kafka_producer(self):
        try:
            producer = KafkaProducer(
                bootstrap_servers=self.kafka_config["bootstrap_servers"],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            logging.info("Kafka Producer for Scanner connected successfully.")
            return producer
        except Exception as e:
            logging.error(f"Failed to connect Kafka Producer: {e}")
            return None

    def perform_scan(self, domain: str) -> dict:
        results = {"domain": domain, "dns": {}, "whois": {}}
        
        try:
            for record_type in ['A', 'AAAA', 'MX', 'NS', 'TXT']:
                answers = dns.resolver.resolve(domain, record_type)
                results["dns"][record_type] = [str(rdata) for rdata in answers]
        except Exception as e:
            results["dns"]["error"] = str(e)

        try:  
            w = whois.whois(domain)
            results["whois"] = {k: str(v) for k, v in w.items()}
        except Exception as e:
            results["whois"]["error"] = str(e)
            
        return results

    def run(self):
        if not self.consumer or not self.producer:
            logging.error("Service cannot run without Kafka connection. Exiting.")
            return

        logging.info(f"{self.service_name} is running and waiting for messages...")
        for message in self.consumer:
            data = message.value
            domain = data.get("domain")
            if not domain:
                continue
            
            logging.info(f"Received message. Scanning domain: {domain}")
            scan_result = self.perform_scan(domain)
            
            logging.info(f"Scan finished. Publishing results for {domain}.")
            self.producer.send(self.kafka_config["result_topic"], value=scan_result)
            self.producer.flush()

if __name__ == "__main__":
    # Pequeña espera para que Kafka esté listo en Docker Compose
    time.sleep(15)
    service = ScannerService(config_path="../config.json")
    service.run()