# Set Up the Basic System
FROM python:3-alpine

# Mount the host directory
COPY . /opt/django
WORKDIR /opt/django

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Get Packages and Other Dependencies
RUN apk add -u zlib-dev jpeg-dev gcc musl-dev
RUN pip install -r /opt/django/requirements.txt gunicorn supervisor

EXPOSE 8000
CMD ["gunicorn", "-c ./deploy/gunicorn.conf.py", ""]