from django.conf.urls.static import static
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.timezone import now

from markdown import markdown


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
    hr_image = models.ImageField(blank=True)
    post_border_image = models.ImageField(blank=True)
    navigation_spritesheet = models.ImageField(blank=True)
    spinner_image = models.ImageField(
        blank=True, help_text="A square PNG that can spin about its center. Ideally 120x120px.")
    favicon_image = models.ImageField(
        blank=True, help_text="A square PNG to be used as a favicon. Ideally 192x192px.")
    font = models.FileField(blank=True)
    background = models.TextField(
        default="white", help_text="a valid CSS `background` configuration")
    overflow = models.TextField(
        default="white", help_text="a valid CSS `background` configuration")

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

    def get_absolute_url(self):
        return reverse("reader-redirect", kwargs={"comic": self.slug})

    def __str__(self):
        return self.title

    def clean(self):
        if AliasUrl.objects.filter(domain=self.domain):
            raise ValidationError("Comic cannot have the same domain as an AliasUrl.")
        if IndexUrl.objects.filter(domain=self.domain):
            raise ValidationError("Comic cannot have the same domain as an IndexUrl.")
        return super().clean()


class TagType(models.Model):
    comic = models.ForeignKey(Comic, on_delete=models.CASCADE, related_name="tag_types")
    title = models.CharField(max_length=16)  # TODO: Make sure this is URL-safe?
    default_icon = models.ImageField(blank=True, help_text="Tags without an image will use this instead.")

    def __str__(self):
        return f"{self.title} ({self.comic})"

    class Meta:
        unique_together = (('comic', 'title'), )
        ordering = ('title', )

    def get_absolute_url(self):
        return reverse("tagtype", kwargs={
            "comic": self.comic.slug,
            "type": self.title
        })


class Tag(models.Model):
    icon = models.ImageField(
        blank=True, null=True, help_text="This image needs to be a 1:1 aspect ratio.")  # TODO: Recommended pixel size
    title = models.CharField(max_length=32)  # TODO: Make sure this is URL-safe?
    type = models.ForeignKey(TagType, on_delete=models.CASCADE, related_name="tags")
    post = models.TextField(blank=True, help_text="Accepts Markdown")

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

    def get_absolute_url(self):
        return reverse("tag", kwargs={
            "comic": self.type.comic.slug,
            "type": self.type.title,
            "tag": self.title,
        })


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
            "comic": self.comic.slug,
            "page": self.slug,
        })

    def __str__(self):
        return f'{self.comic} | {self.title}'

    def transcript_html(self):
        return markdown(self.transcript)


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
