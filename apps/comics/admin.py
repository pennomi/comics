from django.contrib import admin
from django.utils.safestring import mark_safe

from apps.comics.models import Comic, Page, TagType, Tag, Ad, AliasUrl, IndexUrl, StyleConfiguration, \
    LinkedSocialPlatform, SocialPlatform


admin.site.register(TagType)
admin.site.register(AliasUrl)
admin.site.register(IndexUrl)
admin.site.register(SocialPlatform)


class StyleInline(admin.TabularInline):
    model = StyleConfiguration
    extra = 1


class SocialPlatformInline(admin.TabularInline):
    model = LinkedSocialPlatform
    extra = 1


@admin.register(Comic)
class ComicAdmin(admin.ModelAdmin):
    inlines = (StyleInline, SocialPlatformInline, )


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'ordering', 'comic', 'post_transcript_alt', 'tag_list')
    list_filter = ('comic', 'tags')
    filter_horizontal = ('tags', )
    search_fields = ('title', 'slug', )

    def post_transcript_alt(self, obj):
        post = "✓" if obj.post else "✗"
        transcript = "✓" if obj.transcript else "✗"
        alt_text = "✓" if obj.alt_text else "✗"
        return post + transcript + alt_text

    def tag_list(self, obj):
        return ", ".join([t.title for t in obj.tags.all()])


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'type')
    list_filter = ('type',)
    search_fields = ('title', )

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
