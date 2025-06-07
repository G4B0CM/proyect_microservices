FROM python:3.9-slim

WORKDIR /code/scanner_service

COPY ./requirements.txt /code/scanner_service/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/scanner_service/requirements.txt

COPY ./app /code/scanner_service/app
COPY ./config.json /code/scanner_service/config.json


CMD ["python", "app/main.py"]