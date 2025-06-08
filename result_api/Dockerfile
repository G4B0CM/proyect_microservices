FROM python:3.9-slim
WORKDIR /code
ENV PYTHONPATH "${PYTHONPATH}:/code"
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app
COPY ./config.json /code/config.json
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]