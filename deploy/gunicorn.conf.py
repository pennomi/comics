import multiprocessing
import os

PROJECT_DIR = os.getenv('DJANGO_PROJECT_DIR')

bind = "0.0.0.0:80"
wsgi_app = f"{PROJECT_DIR}.wsgi"
workers = multiprocessing.cpu_count() * 2 + 1
reload = True

if int(os.getenv('USE_SSL')):
    bind = "0.0.0.0:443"
    certfile = f"/etc/letsencrypt/live/{PROJECT_DIR}/cert.pem"
    keyfile = f"/etc/letsencrypt/live/{PROJECT_DIR}/fullchain.pem"
