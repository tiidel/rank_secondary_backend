FROM python:3.8-alpine

WORKDIR /rank

RUN apk add --no-cache gcc musl-dev linux-headers

RUN pip install --upgrade pip setuptools
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD [ "python manage.py runserver" ]