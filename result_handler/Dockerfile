FROM python:3.9-slim

WORKDIR /code/result_handler

COPY ./requirements.txt /code/result_handler/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/result_handler/requirements.txt

COPY ./app /code/result_handler/app
COPY ./config.json /code/result_handler/config.json

CMD ["python", "app/main.py"]