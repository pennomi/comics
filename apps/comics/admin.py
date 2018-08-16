from django.contrib import admin

from apps.comics.models import Comic, Page

admin.site.register(Comic)
admin.site.register(Page)
