from django.contrib import admin
from django.utils.safestring import mark_safe

from apps.comics.models import Comic, Page, TagType, Tag, Ad, AliasUrl, IndexUrl, StyleConfiguration

admin.site.register(TagType)
admin.site.register(AliasUrl)
admin.site.register(IndexUrl)


class StyleInline(admin.TabularInline):
    model = StyleConfiguration
    extra = 1


@admin.register(Comic)
class ComicAdmin(admin.ModelAdmin):
    inlines = (StyleInline, )


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'ordering', 'comic', 'tag_list')
    list_filter = ('comic', 'tags')
    filter_horizontal = ('tags', )

    def tag_list(self, obj):
        return ", ".join([t.title for t in obj.tags.all()])


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'type')
    list_filter = ('type',)

    def thumbnail(self, obj):
        if obj.icon:
            return mark_safe(f'<img src="{obj.icon.url}" height="20" /> {obj.title}')
        elif obj.icon:
            return mark_safe(f'<img src="{obj.type.default_icon.url}" height="20" /> {obj.title}')
        else:
            return obj.title


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'url', 'comic', 'active',)
    list_editable = ('active',)
    list_filter = ('active', 'comic')

    def thumbnail(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" height="20" />')
