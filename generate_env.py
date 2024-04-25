"""Generate a bash script that sets up environment variables if it doesn't already exist."""
import random


def get_random_string(length, allowed_chars):
    return ''.join(random.choice(allowed_chars) for _ in range(length))


def main():
    filepath = 'project.env'
    try:
        open(filepath, 'r')
        print(f"Environment file `{filepath}` already found. Skipping file generation.")
    except FileNotFoundError:
        response = ""
        while response not in ("y", "n"):
            response = input("Is this a dev environment (disable SSL and enable debug mode)? (y/N) ").strip().lower()
            if response == "":
                response = "n"
        if response == "y":
            debug_string = "DJANGO_DEBUG=1\nUSE_SSL=0"
        else:
            debug_string = "DJANGO_DEBUG=0\nUSE_SSL=1"

        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#%^&*(-_=+)'  # Removed $ because docker compose is stupid
        with open(filepath, 'w') as outfile:
            outfile.write(f'''DJANGO_PROJECT_DIR=comics
DJANGO_SECRET={get_random_string(50, chars)}
{debug_string}
''')
        print("Created environment file successfully.")


if __name__ == "__main__":
    main()
