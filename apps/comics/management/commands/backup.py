import os
from zipfile import ZipFile

from django.core import management
from django.core.management.base import BaseCommand, no_translations


def dump_data(filename):
    print("Writing database records...")
    management.call_command('dumpdata', verbosity=0, output="data.json")

    print("Writing media files...")
    with ZipFile(filename, 'w') as outfile:
        outfile.write('data.json')
        for dirname, subdirs, files in os.walk("deploy/media"):
            outfile.write(dirname)
            for filename in files:
                outfile.write(os.path.join(dirname, filename))

    print("Cleaning up...")
    os.remove('data.json')


def load_data(filename):

    print("Loading media files...")
    with ZipFile(filename, 'r') as infile:
        infile.extractall()

    print("Loading database records...")
    management.call_command('loaddata', 'data.json')

    print("Cleaning up...")
    os.remove('data.json')


class Command(BaseCommand):
    help = """Dump or load a backup archive containing the entire server's data.

    This includes:
     - Database Records
     - Media Files

     Usage: `./manage.py backup [dump|load] (filename.zip)`
    """

    def add_arguments(self, parser):
        parser.add_argument('action', choices=['dump', 'load'], type=str)
        parser.add_argument('filename', type=str)

    @no_translations
    def handle(self, *args, **options):
        action = options['action']
        filename = options['filename']
        if action == 'dump':
            dump_data(filename)
        elif action == 'load':
            load_data(filename)
