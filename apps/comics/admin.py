from django.contrib import admin

from apps.comics.models import Comic, Page, TagType, Tag, Ad


admin.site.register(Comic)
admin.site.register(TagType)
admin.site.register(Ad)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    filter_horizontal = ('tags',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_filter = ('type',)
