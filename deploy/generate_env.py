"""Generate a bash script that sets up environment variables if it doesn't already exist."""
import random


def get_random_string(length, allowed_chars):
    return ''.join(random.choice(allowed_chars) for i in range(length))


filepath = './deploy/django.env'
try:
    open(filepath, 'r')
    print(f"Environment file `{filepath}` already found. Skipping file generation.")
except FileNotFoundError:
    response = ""
    while response not in ("y", "n"):
        response = input("Is this a dev environment (disable SSL and enable debug mode)? (y/N) ").strip().lower()
        if response == "":
            response = "n"
    debug_string = ""
    if response == "y":
        debug_string = "DJANGO_DEBUG=1"

    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    with open(filepath, 'w') as outfile:
        outfile.write(f'''
DJANGO_SECRET={get_random_string(50, chars)}
PYTHONUNBUFFERED=1
{debug_string}
''')
    print("Created environment file successfully.")
