from django.contrib import admin
from django.utils.safestring import mark_safe
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from apps.comics.models import Comic, Page, TagType, Tag, Ad, AliasUrl, IndexUrl, StyleConfiguration, \
    LinkedSocialPlatform, SocialPlatform, CodeSnippet, HeaderLink

admin.site.register(TagType)
admin.site.register(AliasUrl)
admin.site.register(IndexUrl)
admin.site.register(SocialPlatform)


class HeaderLinkInline(admin.TabularInline):
    model = HeaderLink
    extra = 1


class StyleInline(admin.TabularInline):
    model = StyleConfiguration
    extra = 1


class SocialPlatformInline(admin.TabularInline):
    model = LinkedSocialPlatform
    extra = 1


class SnippetInline(admin.TabularInline):
    model = CodeSnippet
    extra = 1


@admin.register(Comic)
class ComicAdmin(admin.ModelAdmin):
    inlines = (HeaderLinkInline, StyleInline, SocialPlatformInline, SnippetInline,)


@admin.register(CodeSnippet)
class CodeSnippetAdmin(admin.ModelAdmin):
    list_display = ('name', 'comic', 'active', 'testing', 'location',)
    list_filter = ('comic', 'active', 'testing', 'location',)
    list_editable = ('active', 'testing',)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'ordering', 'comic', 'post_transcript_alt', 'tag_list')
    list_filter = ('comic', 'tags')
    filter_horizontal = ('tags',)
    search_fields = ('title', 'slug',)

    def post_transcript_alt(self, obj):
        post = "✓" if obj.post else "✗"
        transcript = "✓" if obj.transcript else "✗"
        alt_text = "✓" if obj.alt_text else "✗"
        return post + transcript + alt_text

    def tag_list(self, obj):
        return ", ".join([t.title for t in obj.tags.all()])


class TagAdminForm(forms.ModelForm):
    pages = forms.ModelMultipleChoiceField(
        queryset=Page.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name='Pages',
            is_stacked=False
        )
    )

    class Meta:
        model = Tag
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['pages'].initial = self.instance.pages.all()

    def save(self, commit=True):
        tag = super().save(commit=False)

        if commit:
            tag.save()

        if tag.pk:
            tag.pages.set(self.cleaned_data['pages'])
            self.save_m2m()

        return tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'type')
    list_filter = ('type',)
    search_fields = ('title',)
    form = TagAdminForm

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
