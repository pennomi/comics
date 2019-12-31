from django.core.management.base import BaseCommand, no_translations


class Command(BaseCommand):
    """Create or renew an SSL certificate for all configured domains.

    HEADS UP! This can only handle up to 100 configured domains. If you need more domains than that, you can fix
    this yourself.
    """

    @no_translations
    def handle(self, *args, **options):
        raise NotImplementedError()
