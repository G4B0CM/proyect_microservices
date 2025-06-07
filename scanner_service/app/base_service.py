# app/base_service.py
import json
from abc import ABC, abstractmethod

class BaseMicroservice(ABC):
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.kafka_config = self.config.get("kafka", {})
        self.service_name = self.config.get("service_name", "UnnamedService")

    def _load_config(self, path: str) -> dict:
        with open(path, 'r') as f:
            return json.load(f)

    @abstractmethod
    def run(self):
        pass