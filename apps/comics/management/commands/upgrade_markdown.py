import re

from django.core.management.base import BaseCommand, no_translations

from apps.comics.models import Page, Tag

SPEAKER_EXTRACTION = re.compile(r'\*\*([\w ]+):\*\*')

class Command(BaseCommand):
    """Create or renew an SSL certificate for all configured domains.

    HEADS UP! This can only handle up to 100 configured domains. If you need more domains than that, you can fix
    this yourself.
    """

    @no_translations
    def handle(self, *args, **options):
        for page in Page.objects.all():
            if not page.transcript:
                continue
            # Extract all "speakers"
            matches = SPEAKER_EXTRACTION.findall(page.transcript)
            for match in matches:
                tag = Tag.objects.filter(title__iexact=match).select_related('type').first()
                if tag:
                    new_syntax = f"<{tag.type.title}:{tag.title}>:"
                    page.transcript = page.transcript.replace(f"**{match}:**", new_syntax)
                    page.save()
                else:
                    new_syntax = "None"
                print(match, tag, new_syntax)
