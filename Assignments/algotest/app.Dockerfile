FROM python:3.8-slim

WORKDIR /fastapi

COPY ./requirements.txt /fastapi/requirements.txt

RUN apt-get update -y && apt-get install -y python3-dev default-libmysqlclient-dev build-essential pkg-config

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /fastapi

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]