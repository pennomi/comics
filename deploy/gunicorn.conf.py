import multiprocessing
import os

PROJECT_DIR = os.getenv('DJANGO_PROJECT_DIR')

bind = "0.0.0.0:8000"
wsgi_app = f"{PROJECT_DIR}.wsgi"
workers = multiprocessing.cpu_count() * 2 + 1
threads = 3
reload = True
accesslog = "-"
