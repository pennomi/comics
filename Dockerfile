# Set Up the Basic System
FROM python:3-alpine

# Mount the host directory
COPY . /opt/django
WORKDIR /opt/django

# Get Packages and Other Dependencies
RUN apk add supervisor nginx certbot vim postgresql-libs bash curl
RUN apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev jpeg-dev zlib-dev
RUN pip install -r /opt/django/requirements.txt gunicorn

# Set environment variables
RUN python ./deploy/generate_env.py

EXPOSE 8000
EXPOSE 80
EXPOSE 443
