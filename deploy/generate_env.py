"""Generate a bash script that sets up environment variables if it doesn't already exist."""

from django.utils.crypto import get_random_string

filepath = './deploy/django.env'
try:
    open(filepath, 'r')
except FileNotFoundError:
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    with open(filepath, 'w') as outfile:
        outfile.write(f'''
DJANGO_SECRET={get_random_string(50, chars)}
PYTHONUNBUFFERED=1
''')
