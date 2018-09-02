# Set Up the Basic System
FROM ubuntu:bionic
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive


# Mount the host directory
COPY . /opt/django
WORKDIR /opt/django

# Get Packages and Other Dependencies
RUN apt-get update
RUN apt-get install -y software-properties-common vim curl python3 python3-venv python3-pip supervisor nginx
RUN add-apt-repository ppa:certbot/certbot
RUN apt-get update
RUN apt-get install -y python-certbot-nginx
RUN python3 -m pip install -r /opt/django/requirements.txt

# Set Up Gunicorn
RUN python3 -m pip install gunicorn
COPY comics/supervisor.conf /etc/supervisor/conf.d/gunicorn.conf

# Set Up Nginx
COPY comics/nginx.conf /etc/nginx/nginx.conf
RUN nginx

EXPOSE 8000
EXPOSE 80
