# app/main.py
import json
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from kafka import KafkaProducer
from .base_service import BaseMicroservice

logging.basicConfig(level=logging.INFO)

class ScanRequest(BaseModel):
    domain: str

class ApiGatewayService(BaseMicroservice):
    def __init__(self, config_path: str, app: FastAPI):
        super().__init__(config_path)
        self.app = app
        self.producer = self._setup_kafka_producer()
        self._register_routes()

    def _setup_kafka_producer(self):
        try:
            producer = KafkaProducer(
                bootstrap_servers=self.kafka_config["bootstrap_servers"],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            logging.info("Kafka Producer for API Gateway connected successfully.")
            return producer
        except Exception as e:
            logging.error(f"Failed to connect Kafka Producer: {e}")
            return None

    def _register_routes(self):
        @self.app.post("/scan", status_code=202)
        async def request_scan(request: ScanRequest):
            if not self.producer:
                raise HTTPException(status_code=500, detail="Kafka is not available")
            
            logging.info(f"Received scan request for domain: {request.domain}")
            
            message = {"domain": request.domain}
            self.producer.send(self.kafka_config["request_topic"], value=message)
            self.producer.flush()
            
            return {"message": "Scan request accepted and is being processed."}

    def run(self):
        import uvicorn
        uvicorn.run(self.app, host="0.0.0.0", port=8000)

app = FastAPI()
service = ApiGatewayService(config_path="../config.json", app=app)

if __name__ == "__main__":
    service.run()