from django.db import models
from django.utils.timezone import now


class Comic(models.Model):
    title = models.CharField(max_length=128)
    slug = models.CharField(max_length=128, unique=True)
    author = models.CharField(max_length=128, blank=True)
    header_image = models.ImageField(blank=True)
    hr_image = models.ImageField(blank=True)
    post_border_image = models.ImageField(blank=True)
    navigation_spritesheet = models.ImageField(blank=True)
    font = models.FileField(blank=True)
    background = models.TextField(
        default="white",
        help_text="a valid CSS `background` configuration")
    overflow = models.TextField(
        default="white",
        help_text="a valid CSS `background` configuration")

    # Social Links
    patreon_link = models.URLField(blank=True)
    discord_link = models.URLField(blank=True)
    reddit_link = models.URLField(blank=True)
    twitter_link = models.URLField(blank=True)
    instagram_link = models.URLField(blank=True)

    def __str__(self):
        return self.title


class TagType(models.Model):
    comic = models.ForeignKey(Comic, on_delete=models.CASCADE)
    title = models.CharField(max_length=16)  # TODO: Make sure this is URL-safe?

    def __str__(self):
        return f"{self.title} ({self.comic})"

    class Meta:
        unique_together = (('comic', 'title'), )


class Tag(models.Model):
    comic = models.ForeignKey(Comic, on_delete=models.CASCADE)
    icon = models.ImageField(
        blank=True, null=True, help_text="This image needs to be a 1:1 aspect ratio.")  # TODO: Recommended pixel size
    title = models.CharField(max_length=32)  # TODO: Make sure this is URL-safe?
    type = models.ForeignKey(TagType, on_delete=models.CASCADE)
    post = models.TextField(blank=True, help_text="Accepts Markdown")

    def __str__(self):
        return self.title

    class Meta:
        unique_together = (('type', 'title'), )


class Page(models.Model):
    comic = models.ForeignKey(Comic, on_delete=models.PROTECT)
    slug = models.CharField(max_length=32)
    title = models.CharField(max_length=128)
    ordering = models.FloatField()
    posted_at = models.DateTimeField(
        default=now, help_text="If this is in the future, it won't be visible until that time")
    post = models.TextField(blank=True, help_text="Accepts Markdown")
    transcript = models.TextField(blank=True, help_text="Accepts Markdown")
    image = models.ImageField()
    alt_text = models.CharField(max_length=150, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="pages")

    class Meta:
        unique_together = (("comic", "slug"), ("comic", "ordering"), )

    def __str__(self):
        return f'{self.comic} - {self.title}'
