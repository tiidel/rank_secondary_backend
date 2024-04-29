FROM surnet/alpine-python-wkhtmltopdf:3.9.2-0.12.6-full

WORKDIR /rank

ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apk update && apk add --no-cache \
    postgresql-client \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    redis \
    fontconfig \
    libxrender \
    libxext \
    libx11 \
    freetype \
    ttf-dejavu \
    ttf-droid \
    ttf-freefont \
    ttf-liberation \
    wget \
    tar \
    xz

    

# Upgrade pip and setuptools
RUN pip install --no-cache-dir --upgrade pip setuptools

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 6379

CMD ["python", "run.py", "runserver", "0.0.0.0:8000"]
