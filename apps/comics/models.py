from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.timezone import now

from apps.comics import custom_markdown


class Comic(models.Model):
    # Routing information
    domain = models.CharField(
        max_length=128, unique=True, blank=True,
        help_text="The domain used to view this comic, in the format `subdomain.example.com`. "
                  "If this is blank, the comic will not be able to be viewed.")
    slug = models.CharField(max_length=128, unique=True, help_text="Deprecated.")

    # Comic information
    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    author = models.CharField(max_length=128, blank=True)
    genre = models.CharField(max_length=64, blank=True)

    # Style & Images
    # TODO: Add documentation on preferred pixel sizes
    header_image = models.ImageField(blank=True)
    post_border_image = models.ImageField(blank=True)
    navigation_spritesheet = models.ImageField(blank=True)
    spinner_image = models.ImageField(
        blank=True, help_text="A square PNG that can spin about its center. Ideally 120x120px.")
    favicon_image = models.ImageField(
        blank=True, help_text="A square PNG to be used as a favicon. Ideally 192x192px.")
    overflow_background_image = models.ImageField(
        blank=True, help_text="A large JPG. Ideally 2048px wide by 1024px tall or larger.")
    font = models.FileField(blank=True)
    background = models.TextField(
        default="white", help_text="a valid CSS `background` configuration")
    overflow = models.TextField(
        default="white", help_text="a valid CSS `background` configuration")
    error_404_image = models.ImageField(
        blank=True, help_text="A square PNG to be used as a 404 message. Ideally 1000x1000px.")
    error_500_image = models.ImageField(
        blank=True, help_text="A square PNG to be used as a 500 message. Ideally 1000x1000px.")

    # Social Links
    patreon_link = models.URLField(blank=True)
    discord_link = models.URLField(blank=True)
    reddit_link = models.URLField(blank=True)
    twitter_link = models.URLField(blank=True)
    instagram_link = models.URLField(blank=True)

    # Third-party integrations
    # TODO: Add Google Analytics
    adsense_publisher_account = models.CharField(
        max_length=32, blank=True, help_text="Looks like `pub-1234567891234567`")
    adsense_ad_slot = models.CharField(
        max_length=10, blank=True, help_text="Looks like `1234567890`")
    discourse_url = models.URLField(
        blank=True, help_text="Link to a Discourse forum, for example `https://forum.example.com/`")

    # Misc
    changed_at = models.DateTimeField(auto_now=True, help_text="Records the last edit of this Comic.")

    def get_absolute_url(self):
        return reverse("reader-redirect")

    def __str__(self):
        return self.title

    def clean(self):
        if AliasUrl.objects.filter(domain=self.domain):
            raise ValidationError("Comic cannot have the same domain as an AliasUrl.")
        if IndexUrl.objects.filter(domain=self.domain):
            raise ValidationError("Comic cannot have the same domain as an IndexUrl.")
        return super().clean()


class CssPropertyChoices(models.TextChoices):
    overflow_background = 'overflow-background'
    content_background = 'content-background'
    primary_text_color = 'primary-text-color'
    footer_background_color = 'footer-background-color'
    tag_background_color = 'tag-background-color'
    tag_text_color = 'tag-text-color'

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

    def __str__(self):
        return f"{self.title} ({self.comic})"

    class Meta:
        unique_together = (('comic', 'title'), )
        ordering = ('title', )

    def get_absolute_url(self):
        return reverse("archive-tagtype", kwargs={
            "type": self.title
        })


class Tag(models.Model):
    icon = models.ImageField(
        blank=True, null=True, help_text="This image needs to be a 1:1 aspect ratio.")  # TODO: Recommended pixel size
    title = models.CharField(max_length=32)  # TODO: Make sure this is URL-safe?
    type = models.ForeignKey(TagType, on_delete=models.CASCADE, related_name="tags")
    post = models.TextField(blank=True, help_text="Accepts Markdown")
    changed_at = models.DateTimeField(auto_now=True, help_text="Records the last edit of this Tag.")

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

#
# @receiver(post_save, sender=Tag, dispatch_uid="migrate_tags")
# def update_stock(sender, instance, **kwargs):
#     instance.product.stock -= instance.amount
#     instance.product.save()


class PageQuerySet(models.QuerySet):
    def active(self):
        return self.filter(posted_at__lte=now())


class Page(models.Model):
    """A Page is a single image of a Comic, with associated position (ordering) data."""
    comic = models.ForeignKey(Comic, on_delete=models.PROTECT, related_name="pages")
    slug = models.CharField(max_length=32)
    title = models.CharField(max_length=128)
    ordering = models.FloatField(
        help_text="Lower numbers appear first. You can use negative numbers and decimals (eg. -2.5).")
    posted_at = models.DateTimeField(
        default=now, help_text="If this is in the future, it won't be visible until that time.")
    changed_at = models.DateTimeField(auto_now=True, help_text="Records the last edit of this Page.")
    post = models.TextField(blank=True, help_text="Accepts Markdown")
    transcript = models.TextField(blank=True, help_text="Accepts Markdown")
    image = models.ImageField()
    alt_text = models.CharField(max_length=150, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="pages")

    objects = PageQuerySet.as_manager()

    class Meta:
        unique_together = (("comic", "slug"), ("comic", "ordering"), )
        ordering = ('ordering', )

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


class Ad(models.Model):
    """Ad objects show a custom banner at the bottom of the comic."""
    comic = models.ForeignKey(Comic, on_delete=models.PROTECT, related_name="ads")
    image = models.ImageField()
    url = models.URLField()
    active = models.BooleanField(
        default=True, help_text="The ad shown on the page is randomly chosen from all active ads.")

    def __str__(self):
        return f'{self.comic} | {self.url}'


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
        if IndexUrl.objects.filter(domain=self.domain):
            raise ValidationError("AliasUrl cannot have the same domain as an IndexUrl.")
        super().clean()


class IndexUrl(models.Model):
    """This model exists for ensuring automatic SSL is generated for the index domains."""

    domain = models.CharField(
        max_length=128, unique=True,
        help_text="Any request going to this domain will be shown the comic index pages.")

    def __str__(self):
        return f'{self.domain}'

    def clean(self):
        if Comic.objects.filter(domain=self.domain):
            raise ValidationError("IndexUrl cannot have the same domain as a Comic.")
        if AliasUrl.objects.filter(domain=self.domain):
            raise ValidationError("IndexUrl cannot have the same domain as an AliasUrl.")
        super().clean()
