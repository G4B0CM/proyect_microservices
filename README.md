# Microservice-Based Domain Scanner

This project is an educational example of a microservices architecture designed to scan web domains for public information. It leverages Python, FastAPI, Kafka, and Docker to create a decoupled, asynchronous, and scalable system.

A user submits a domain through a web interface. The request is processed through a series of independent services communicating via a Kafka message bus, and the final results are displayed back to the user on the web page.

## Core Concepts Illustrated
- **Microservices Architecture**: Each component (API Gateway, Scanner, Results API) is an independent service.
- **Asynchronous Communication**: Services communicate via Kafka, allowing them to work without waiting for each other.
- **Decoupling**: Services are not directly dependent on each other, only on the message bus (Kafka).
- **Configuration Management**: Sensitive data like connection strings are kept out of the code and managed in configuration files.
- **Containerization**: The entire system is containerized with Docker and orchestrated with Docker Compose for easy setup and deployment.
- **API Design**: Utilizes FastAPI for building robust and modern APIs.
- **Frontend-Backend Interaction**: Demonstrates how a frontend can interact with an asynchronous backend using a polling mechanism.

## System Architecture

The system is composed of the following services:

1.  **Frontend**: A simple static web page (HTML/JS) served by Nginx. It provides the user interface to submit a domain for scanning.
2.  **API Gateway (`api-gateway`)**: A FastAPI application that serves as the single entry point for the system. It receives the scan request, validates it, and publishes a message to a Kafka topic.
3.  **Scanner Service (`scanner-service`)**: A Python worker that listens to scan requests on a Kafka topic. It performs the domain analysis (DNS, WHOIS lookups) and publishes the results to another Kafka topic.
4.  **Results API (`result-api`)**: A FastAPI application that consumes the scan results from Kafka, stores them in memory, and exposes a REST endpoint for the frontend to poll for the results.
5.  **Kafka & Zookeeper**: The message bus that enables asynchronous communication between the services.

### Data Flow

User -> (HTTP) -> [Frontend] -> (HTTP POST) -> [API Gateway]
|
v (Produce Message)
[Kafka Topic: domain_scan_requests]
|
v (Consume Message)
[Scanner Service]
|
v (Produce Message)
[Kafka Topic: domain_scan_results]
|
v (Consume Message)
[Results API] <-- (HTTP GET - Polling) -- [Frontend]
## Prerequisites
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Getting Started

Follow these steps to set up and run the project locally.

### 1. Clone the Repository

git clone https://github.com/G4B0CM/proyect_microservices 
cd microservice-based-domain-scanner

2. Create Configuration Files
For security reasons, configuration files (*.json) are not committed to the repository. You must create them manually in each service's directory.
API Gateway Configuration
Create a file named api-gateway/config.json with the following content:
{
  "service_name": "API Gateway",
  "kafka": {
    "bootstrap_servers": "kafka:9092",
    "request_topic": "domain_scan_requests"
  }
}

Scanner Service Configuration
Create a file named scanner-service/config.json with the following content:
{
  "service_name": "Scanner Service",
  "kafka": {
    "bootstrap_servers": "kafka:9092",
    "request_topic": "domain_scan_requests",
    "result_topic": "domain_scan_results",
    "consumer_group_id": "scanner_group"
  }
}

Results API Configuration
Create a file named result-api/config.json with the following content:
{
  "service_name": "Result API",
  "kafka": {
    "bootstrap_servers": "kafka:9092",
    "result_topic": "domain_scan_results",
    "consumer_group_id": "result_api_group"
  }
}

Note: The bootstrap_servers value kafka:9092 refers to the service name defined in docker-compose.yml. Docker's internal DNS will resolve this name to the correct container IP address.
3. Build and Run the System
From the root directory of the project, run the following command. The --build flag ensures that Docker images are built from scratch.
  docker-compose up --build
Docker Compose will build the images for each service and start all containers. You will see logs from all services in your terminal. Wait until you see messages indicating that the services have successfully connected to Kafka.

4. Use the Application
Open your web browser and navigate to http://localhost:8080.
You will see the domain scanner interface.
Enter a domain name (e.g., google.com) and click the "Escanear" (Scan) button.
The status message will update, indicating that the request has been accepted and that it is polling for results.
After a few seconds, the complete scan result will be displayed on the page in JSON format.
Stopping the System
To stop all running containers, press Ctrl+C in the terminal where docker-compose is running. To remove the containers and the network, run:
docker-compose down


Project Structure
.
├── api-gateway/         # Handles incoming API requests
│   ├── app/
│   ├── config.json.example  # Example config file
│   └── Dockerfile
├── frontend/            # Static web UI
│   ├── index.html
│   ├── nginx.conf
│   └── Dockerfile
├── result-api/          # Stores and serves scan results
│   ├── app/
│   ├── config.json.example
│   └── Dockerfile
├── scanner-service/     # Performs the domain scan
│   ├── app/
│   ├── config.json.example
│   └── Dockerfile
├── .gitignore
├── docker-compose.yml   # Orchestrates all services
└── README.md

I recommend you also create the config.json.example files mentioned in the structure above. They would contain the same content as the config.json files, serving as clear templates for anyone setting up the project.
