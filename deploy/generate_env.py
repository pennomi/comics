"""Generate a bash script that sets up environment variables if it doesn't already exist."""
import random


def get_random_string(length, allowed_chars):
    ''.join(random.choice(allowed_chars) for i in range(length))


filepath = './deploy/django.env'
try:
    open(filepath, 'r')
except FileNotFoundError:
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    with open(filepath, 'w') as outfile:
        outfile.write('''
DJANGO_SECRET={}
PYTHONUNBUFFERED=1
'''.format(get_random_string(50, chars)))
