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
RUN pip install -r /opt/django/requirements.txt gunicorn certbot

# Make things executable
RUN chmod +x ./generate_env.py
RUN chmod +x ./run_server.sh

EXPOSE 80
EXPOSE 443

CMD ["gunicorn", "-c ./deploy/gunicorn.conf.py", ""]