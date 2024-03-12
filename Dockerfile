FROM python:3.8-alpine

WORKDIR /rank

ENV PYTHONUNBUFFERED=1
RUN apk update && apk add postgresql-client

RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev redis

RUN pip install --upgrade pip setuptools

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 6379

CMD ["python", "run.py", "runserver", "0.0.0.0:8000"]
