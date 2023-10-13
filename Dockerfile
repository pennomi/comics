# Set Up the Basic System
# TODO: Try python3-alpine?
FROM python:3-slim

# Mount the host directory
COPY . /opt/django
WORKDIR /opt/django

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Get Packages and Other Dependencies
# RUN apt update && apt install -y nginx
RUN pip install -r /opt/django/requirements.txt gunicorn supervisor

EXPOSE 8000
CMD ["gunicorn", "-c ./deploy/gunicorn.conf.py", ""]