import os
from django.core.management.base import BaseCommand, no_translations
from django.core.files import File

from apps.comics.models import Page


class Command(BaseCommand):
    @no_translations
    def handle(self, *args, **options):
        thumbnails = os.listdir("thumbs")

        for thumb in thumbnails:
            if not thumb.endswith(".png"):
                continue

            comic_number = float(thumb.split(".")[0])
            try:
                page = Page.objects.get(comic__title="Swords", ordering=comic_number)
                print(thumb, page)
                with open(f"thumbs/{thumb}", "rb") as img_file:
                    page.thumbnail.save(thumb, File(img_file))
            except Page.DoesNotExist:
                continue
