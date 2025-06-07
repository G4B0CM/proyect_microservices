FROM python:3.9-slim

WORKDIR /code/api_gateway

COPY ./requirements.txt /code/api_gateway/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/api_gateway/requirements.txt

COPY ./app /code/api_gateway/app
COPY ./config.json /code/api_gateway/config.json

CMD ["python", "app/main.py"]