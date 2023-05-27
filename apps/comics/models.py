from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.urls import reverse
from django.utils.timezone import now

from apps.comics import custom_markdown
from apps.comics.cloudflare_utilities import purge_paths, build_resize_url


class Comic(models.Model):
    # Routing information
    domain = models.CharField(
        max_length=128, unique=True, blank=True,
        help_text="The domain used to view this comic, in the format `subdomain.example.com`. "
                  "If this is blank, the comic will not be able to be viewed.")

    # Comic information
    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    author = models.CharField(max_length=128, blank=True)
    genre = models.CharField(max_length=64, blank=True)

    # Style & Images
    # TODO: Add documentation on preferred pixel sizes
    header_image = models.ImageField(blank=True)
    secret_image = models.ImageField(blank=True, help_text="Shows up when the user inputs the Konami code")
    post_border_image = models.ImageField(blank=True)
    navigation_spritesheet = models.ImageField(blank=True)
    spinner_image = models.ImageField(
        blank=True, help_text="A square PNG that can spin about its center. Ideally 120x120px.")
    favicon_image = models.ImageField(
        blank=True, help_text="A square PNG to be used as a favicon. Ideally 192x192px.")
    overflow_background_image = models.ImageField(
        blank=True, help_text="A large JPG. Ideally 2048px wide by 1024px tall or larger.")
    archive_icon = models.ImageField(
        blank=True, help_text="A square PNG to be used as an archive/pages icon.")
    font = models.FileField(blank=True)
    background = models.TextField(
        default="white", help_text="a valid CSS `background` configuration")
    overflow = models.TextField(
        default="white", help_text="a valid CSS `background` configuration")
    error_404_image = models.ImageField(
        blank=True, help_text="A square PNG to be used as a 404 message. Ideally 1000x1000px.")
    error_500_image = models.ImageField(
        blank=True, help_text="A square PNG to be used as a 500 message. Ideally 1000x1000px.")

    # Misc configuration
    quests_tab_title = models.CharField(max_length=16, default="Quests")

    # Third-party integrations
    discourse_url = models.URLField(
        blank=True, help_text="Link to a Discourse forum, for example `https://forum.example.com/`")
    cloudflare_token = models.CharField(max_length=50, blank=True, help_text="Your Cloudflare API Token")
    cloudflare_zone = models.CharField(max_length=50, blank=True, help_text="Your Cloudflare Zone ID")
    cloudflare_resize = models.BooleanField(
        default=False, help_text="If True, resize images using CloudFlare's API. (Requires paid account.)")

    # Misc
    changed_at = models.DateTimeField(auto_now=True, help_text="Records the last edit of this Comic.")

    def get_absolute_url(self):
        return reverse("reader-redirect")

    def __str__(self):
        return self.title

    def clean(self):
        if AliasUrl.objects.filter(domain=self.domain):
            raise ValidationError("Comic cannot have the same domain as an AliasUrl.")
        return super().clean()

    @staticmethod
    def clear_cache(sender, instance, **kwargs):
        purge_paths(instance, [], everything=True)


post_save.connect(Comic.clear_cache, Comic)


class HeaderLinkManager(models.Manager):
    def active(self):
        return self.filter(active=True)


class HeaderLink(models.Model):
    """Customizable Links that appear in the header."""
    text = models.CharField(max_length=24, help_text="The text the user should see. Keep this short!")
    comic = models.ForeignKey(Comic, on_delete=models.CASCADE, related_name="header_links")
    active = models.BooleanField(default=True, help_text="Disable this to remove the injected code from the page.")
    ordering = models.FloatField(default=0, help_text="The order in which the links are shown. Smaller is shown first.")
    url = models.URLField(help_text="The URL you want to send people to.")

    objects = HeaderLinkManager()

    class Meta:
        ordering = ('ordering', )

    def __str__(self):
        return f"{self.comic} - {self.text}"


class ShortCodeRedirect(models.Model):
    """Short URLs for redirecting to other places. For example, https://comic.example.com/patreon -> your Patreon URL"""
    comic = models.ForeignKey(Comic, on_delete=models.CASCADE, related_name="short_codes")
    short_code = models.CharField(max_length=24, help_text="The uri you want on the comics side, eg. 'patreon'")
    url = models.URLField(help_text="The URL you want to send people to.")


class SnippetQuerySet(models.QuerySet):
    def for_comic(self, comic):
        return self.filter(
            Q(comic=comic) | Q(comic=None),
            active=True
        )


class CodeSnippet(models.Model):
    """Arbitrary HTML code that gets injected into the main comics pages."""

    name = models.CharField(
        max_length=32, help_text="Human-readable name for this injected code.")
    comic = models.ForeignKey(
        Comic, null=True, blank=True, on_delete=models.CASCADE, related_name="code_snippets",
        help_text="Which comic does this snippet appear on? Leave blank for all comics.")
    active = models.BooleanField(default=True, help_text="Disable this to remove the injected code from the page.")
    testing = models.BooleanField(
        default=False, help_text="When this is active, it is only embedded on the test URL page.")
    location = models.PositiveSmallIntegerField(default=0, choices=(
        (0, 'Start of Head'),
        (1, 'End of Body'),
        (2, 'Inside Header Ad Slot'),
        (3, 'Inside Below Comic Ad Slot'),
        (4, 'Inside Below Info Ad Slot'),
    ), help_text="The location in the document where the code will be injected.")
    code = models.TextField(
        blank=True, help_text="The HTML code that is injected into the page. "
                              "BE CAREFUL -- this code can break your site if you don't know what you are doing!")

    objects = SnippetQuerySet.as_manager()

    def __str__(self):
        return f"{self.comic or 'Global'} - {self.name}"

    @staticmethod
    def clear_cache(sender, instance, **kwargs):
        Comic.clear_cache(sender, instance.comic, **kwargs)


post_save.connect(CodeSnippet.clear_cache, CodeSnippet)


class CssPropertyChoices(models.TextChoices):
    overflow_background = 'overflow-background'
    content_background = 'content-background'
    primary_text_color = 'primary-text-color'
    footer_background_color = 'footer-background-color'
    tag_background_color = 'tag-background-color'
    tag_text_color = 'tag-text-color'
    tab_inactive_color = 'tab-inactive-color'
    tab_active_color = 'tab-active-color'
    tab_text_color = 'tab-text-color'

    spinner_image = 'spinner-image'
    navigation_spritesheet = 'navigation-spritesheet'
    post_border_image = 'post-border-image'  # TODO: Border image width?


class StyleConfiguration(models.Model):
    """StyleConfiguration objects make it easy to override CSS rules in a safe way."""
    comic = models.ForeignKey(Comic, on_delete=models.CASCADE, related_name="style_configurations")
    property = models.CharField(
        max_length=32, choices=CssPropertyChoices.choices,
        help_text="Use CSS property values. For colors, that's like `#000000FF` and for images "
                  "that's like `url(https://placekitten.com/120/120/)`")
    value = models.CharField(max_length=128)  # TODO: Validate that there's no CSS injection

    def __str__(self):
        return f"--{self.property}: {self.value};"

    class Meta:
        unique_together = (('comic', 'property'),)


class TagType(models.Model):
    comic = models.ForeignKey(Comic, on_delete=models.CASCADE, related_name="tag_types")
    title = models.CharField(max_length=16)  # TODO: Make sure this is URL-safe?
    default_icon = models.ImageField(blank=True, help_text="Tags without an image will use this instead.")
    changed_at = models.DateTimeField(auto_now=True, help_text="Records the last edit of this TagType.")
    ad_override = models.ForeignKey(
        'comics.Ad', on_delete=models.SET_NULL, null=True, blank=True,
        help_text="If not blank, this ad will be shown on this tag page. HEADS UP! It will show even if deactivated!")

    def __str__(self):
        return f"{self.title} ({self.comic})"

    class Meta:
        unique_together = (('comic', 'title'), )
        ordering = ('title', )

    def get_absolute_url(self):
        return reverse("archive-tagtype", kwargs={
            "type": self.title
        })

    @property
    def best_icon(self):
        most_used_tag = self.tags.annotate(count=models.Count('pages')).order_by("-count", 'title').first()
        return most_used_tag.icon_url

    @staticmethod
    def clear_cache(sender, instance, **kwargs):
        Comic.clear_cache(sender, instance.comic, **kwargs)


post_save.connect(TagType.clear_cache, TagType)


class Tag(models.Model):
    icon = models.ImageField(
        blank=True, null=True, help_text="This image needs to be a 1:1 aspect ratio.")  # TODO: Recommended pixel size
    title = models.CharField(max_length=32)  # TODO: Make sure this is URL-safe?
    type = models.ForeignKey(TagType, on_delete=models.CASCADE, related_name="tags")
    post = models.TextField(blank=True, help_text="Accepts Markdown")
    changed_at = models.DateTimeField(auto_now=True, help_text="Records the last edit of this Tag.")
    ad_override = models.ForeignKey(
        'comics.Ad', on_delete=models.SET_NULL, null=True, blank=True,
        help_text="If not blank, this ad will be shown on this tag page. HEADS UP! It will show even if deactivated!")

    def __str__(self):
        return self.title

    class Meta:
        unique_together = (('type', 'title'), )
        ordering = ('type', 'title', )

    @property
    def icon_url(self):
        if self.icon:
            return self.icon.url
        elif self.type.default_icon:
            return self.type.default_icon.url
        else:
            return None

    @property
    def post_html(self):
        return custom_markdown.render(self.post)

    def get_absolute_url(self):
        return reverse("archive-tag", kwargs={
            "type": self.type.title,
            "tag": self.title,
        })

    @staticmethod
    def clear_cache(sender, instance, **kwargs):
        Comic.clear_cache(sender, instance.type.comic, **kwargs)


post_save.connect(Tag.clear_cache, Tag)


class PageQuerySet(models.QuerySet):
    def active(self):
        return self.filter(posted_at__lte=now())


class Page(models.Model):
    def get_image_file_path(self, filename):
        return f"{self.comic.title}/images/{filename}"

    def get_thumbnail_file_path(self, filename):
        return f"{self.comic.title}/thumbnails/{filename}"

    """A Page is a single image of a Comic, with associated position (ordering) data."""
    comic = models.ForeignKey(Comic, on_delete=models.PROTECT, related_name="pages")
    slug = models.CharField(max_length=32)
    title = models.CharField(max_length=128)
    ordering = models.FloatField(
        help_text="Lower numbers appear first. You can use negative numbers and decimals (eg. -2.5).")
    chronological_ordering = models.FloatField(
        default=0, help_text="Lower numbers appear first. You can use negative numbers and decimals (eg. -2.5).")
    posted_at = models.DateTimeField(
        default=now, help_text="If this is in the future, it won't be visible until that time.")
    changed_at = models.DateTimeField(auto_now=True, help_text="Records the last edit of this Page.")
    post = models.TextField(blank=True, help_text="Accepts Markdown")
    transcript = models.TextField(blank=True, help_text="Accepts Markdown")
    image = models.ImageField(upload_to=get_image_file_path)
    thumbnail = models.ImageField(upload_to=get_thumbnail_file_path, null=True, blank=True,
                                  help_text="Recommended size: 300x300px")
    alt_text = models.CharField(max_length=150, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="pages")

    objects = PageQuerySet.as_manager()

    class Meta:
        unique_together = (("comic", "slug"), ("comic", "ordering"), )
        ordering = ('ordering', )

    @property
    def resized_image_url(self):
        if self.comic.cloudflare_resize:
            return build_resize_url(self.image.url, 1440)  # 1440 is a size that works on virtually all screens
        return self.image.url

    def get_absolute_url(self):
        return reverse("reader", kwargs={
            "page": self.slug,
        })

    def __str__(self):
        return f'{self.comic} | {self.title}'

    @property
    def post_html(self):
        return custom_markdown.render(self.post)

    @property
    def transcript_html(self):
        return custom_markdown.render(self.transcript)

    @property
    def transcript_txt(self):
        return custom_markdown.render_txt(self.transcript)

    @staticmethod
    def clear_cache(sender, instance, **kwargs):
        Comic.clear_cache(sender, instance.comic, **kwargs)


post_save.connect(Page.clear_cache, Page)


class Chapter(models.Model):
    """
    A Chapter is a section that splits the page list by 'ordering', and used for quick navigation shortcuts.
    It doesn't include an image; use a Page for that.
    """
    comic = models.ForeignKey(Comic, on_delete=models.PROTECT, related_name="chapters")
    title = models.CharField(max_length=128)
    ordering = models.FloatField(
        help_text="Lower numbers appear first. You can use negative numbers and decimals (eg. -2.5).")

    class Meta:
        unique_together = (("comic", "ordering"), )
        ordering = ('ordering', )

    def __str__(self):
        return f'{self.comic} | {self.title}'

    @staticmethod
    def clear_cache(sender, instance, **kwargs):
        purge_paths(instance.comic, [
            reverse("archive-pages"),
        ])


post_save.connect(Chapter.clear_cache, Chapter)


class AdQuerySet(models.QuerySet):
    def active(self, comic):
        return self.filter(comic=comic, active=True).order_by("?").first()


class Ad(models.Model):
    """Ad objects show a custom banner at the bottom of the comic."""
    AD_TYPES = [
        ('Banner', 'Banner'),
        ('Popup', 'Popup'),
    ]

    comic = models.ForeignKey(Comic, on_delete=models.PROTECT, related_name="ads")
    type = models.CharField(max_length=6, choices=AD_TYPES, default="Banner")
    image = models.ImageField()
    url = models.URLField()
    active = models.BooleanField(
        default=True, help_text="The ad shown on the page is randomly chosen from all active ads.")

    objects = AdQuerySet.as_manager()

    def __str__(self):
        return f'{self.comic} | {self.url}'

    @staticmethod
    def clear_cache(sender, instance, **kwargs):
        Comic.clear_cache(sender, instance.comic, **kwargs)


post_save.connect(Ad.clear_cache, Ad)


class AliasUrl(models.Model):
    """AliasUrl objects are used to redirect domains to the canonical URL for the attached Comic object."""

    comic = models.ForeignKey(Comic, on_delete=models.CASCADE, related_name="alias_urls")
    domain = models.CharField(
        max_length=128, unique=True,
        help_text="Any request going to this domain will be redirected to the canonical domain of the comic.")

    def __str__(self):
        return f'{self.domain} → {self.comic}'

    def clean(self):
        if Comic.objects.filter(domain=self.domain):
            raise ValidationError("AliasUrl cannot have the same domain as a Comic.")
        super().clean()


def social_icon_static_path(instance, filename):
    return f'social_icons/{instance.name}/{filename}'


class SocialPlatform(models.Model):
    """This model holds the technical data to attach a social media or other external link.
    To attach it to a Comic, you'll use a LinkedSocialPlatform, configured in the Comic admin.
    """
    name = models.CharField(max_length=32)
    image = models.ImageField(
        blank=True, null=True, upload_to=social_icon_static_path,
        help_text="This icon should be a 1:1 aspect ratio, and should be in color.")
    visit_template = models.CharField(
        max_length=128, blank=True, help_text="Use {handle} for vars.")
    follow_template = models.CharField(
        max_length=128, blank=True,
        help_text="Use {handle} for vars. Leave blank if it doesn't have explicit follow functionality.")
    share_template = models.CharField(
        max_length=128, blank=True,
        help_text="Use {url}, {message} for vars. Leave blank if it doesn't have share functionality.")
    visit_cta = models.CharField(max_length=128, blank=True)
    follow_cta = models.CharField(max_length=128, blank=True)
    share_cta = models.CharField(max_length=128, blank=True)
    requires_money = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class LinkedSocialPlatform(models.Model):
    comic = models.ForeignKey(Comic, on_delete=models.CASCADE, related_name='social_links')
    platform = models.ForeignKey(SocialPlatform, on_delete=models.CASCADE)
    handle = models.CharField(
        max_length=64, blank=True,
        help_text="Leave blank if you have no page; it still needs to be connected for people to share to this "
                  "platform.")
    title = models.CharField(
        max_length=64, blank=True, help_text="If not blank, overrides the platform name.")
    visit_cta = models.CharField(max_length=128, blank=True, help_text="If not blank, overrides the platform CTA.")
    follow_cta = models.CharField(max_length=128, blank=True, help_text="If not blank, overrides the platform CTA.")
    share_cta = models.CharField(max_length=128, blank=True, help_text="If not blank, overrides the platform CTA.")

    @property
    def follow_url(self):
        if not self.handle:
            return ''
        return self.platform.follow_template.format(handle=self.handle)

    @property
    def visit_url(self):
        if not self.handle:
            return ''
        return self.platform.visit_template.format(handle=self.handle)

    def __str__(self):
        return f"{self.comic} - {self.platform}"
