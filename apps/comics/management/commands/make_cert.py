import os
from django.core.management.base import BaseCommand, no_translations


class Command(BaseCommand):
    """Create or renew an SSL certificate for all configured domains.

    HEADS UP! This can only handle up to 100 configured domains. If you need more domains than that, you can fix
    this yourself.
    """

    @no_translations
    def handle(self, *args, **options):
        # TODO: This is unfinished and totally won't work

        print("Creating SSL certificate for configured domains")
        domains = " -d ".join(["example.com", "www.example.com"])

        # Ensure that the letsencrypt folder exists
        os.system("mkdir /var/www/letsencrypt")

        # Tell certbot to make the certificate
        command = f"certbot certonly --cert-name comics --webroot --webroot-path /var/www/letsencrypt -d {domains}"
        os.system(command)
