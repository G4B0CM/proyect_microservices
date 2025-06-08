# app/main.py
import json
import logging
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
# ¡Importación nueva!
from fastapi.middleware.cors import CORSMiddleware
from app.base_service import BaseMicroservice

logging.basicConfig(level=logging.INFO)

class ScanRequest(BaseModel):
    domain: str

app = FastAPI()

# ---- INICIO DE LA CONFIGURACIÓN DE CORS ----

# Lista de orígenes que tienen permiso para hacer solicitudes.
# Para desarrollo, puedes usar un comodín '*' para permitir todos,
# pero es más seguro ser explícito.
origins = [
    "http://localhost",
    "http://localhost:8080", # El origen de tu frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Permite los orígenes en la lista
    allow_credentials=True, # Permite cookies (no aplica aquí, pero es buena práctica)
    allow_methods=["*"],    # Permite todos los métodos (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],    # Permite todas las cabeceras
)

# ---- FIN DE LA CONFIGURACIÓN DE CORS ----


class ApiGatewayService(BaseMicroservice):
    def __init__(self, config_path: str):
        super().__init__(config_path)
        self.producer = self._setup_kafka_producer()
        self._register_routes()

    def _setup_kafka_producer(self):
        retries = 5
        delay = 3
        for i in range(retries):
            try:
                producer = KafkaProducer(
                    bootstrap_servers=self.kafka_config["bootstrap_servers"],
                    value_serializer=lambda v: json.dumps(v).encode('utf-8')
                )
                logging.info("Kafka Producer for API Gateway connected successfully.")
                return producer
            except NoBrokersAvailable:
                logging.warning(f"Kafka not available, retrying in {delay}s... ({i+1}/{retries})")
                time.sleep(delay)
        
        logging.error("Could not connect to Kafka after several retries. Exiting.")
        return None

    def _register_routes(self):
        @app.post("/scan", status_code=202)
        async def request_scan(request: ScanRequest):
            if not self.producer:
                raise HTTPException(status_code=503, detail="Service Unavailable: Kafka is not connected")
            
            logging.info(f"Received scan request for domain: {request.domain}")
            message = {"domain": request.domain}
            self.producer.send(self.kafka_config["request_topic"], value=message)
            self.producer.flush()
            return {"message": "Scan request accepted and is being processed."}

    def run(self):
        pass

service = ApiGatewayService(config_path="config.json")