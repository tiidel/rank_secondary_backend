FROM python:3.8-alpine

WORKDIR /rank

ENV PYTHONUNBUFFERED=1

# Install dependencies
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
    ttf-liberation

# Download and install wkhtmltox
RUN wget -q -O /tmp/wkhtmltox.tar.xz "https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox-0.12.6-1.alpine-3.14-x86_64.tar.xz" && \
    tar -xf /tmp/wkhtmltox.tar.xz -C /usr/local/ && \
    ln -s /usr/local/wkhtmltox/bin/wkhtmltopdf /usr/local/bin/wkhtmltopdf && \
    ln -s /usr/local/wkhtmltox/bin/wkhtmltoimage /usr/local/bin/wkhtmltoimage && \
    rm /tmp/wkhtmltox.tar.xz

# Upgrade pip and setuptools
RUN pip install --upgrade pip setuptools

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 6379

CMD ["python", "run.py", "runserver", "0.0.0.0:8000"]
