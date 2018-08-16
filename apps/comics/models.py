from django.db import models


class Comic(models.Model):
    title = models.CharField(max_length=128)
    slug = models.CharField(max_length=128, unique=True)
    header_image = models.ImageField(blank=True)
    navigation_spritesheet = models.ImageField(blank=True)
    background = models.TextField(
        default="white",
        help_text="a valid CSS `background` configuration")
    overflow = models.TextField(
        default="white",
        help_text="a valid CSS `background` configuration")

    def __str__(self):
        return self.title


class TagType(models.Model):
    comic = models.ForeignKey(Comic, on_delete=models.CASCADE)
    title = models.CharField(max_length=16)


# TODO: This could eventually turn into some kind of wiki-entry thing
class Tag(models.Model):
    comic = models.ForeignKey(Comic, on_delete=models.CASCADE)
    icon = models.ImageField(blank=True, null=True)
    title = models.CharField(max_length=32)
    type = models.ForeignKey(TagType, on_delete=models.CASCADE)


class Page(models.Model):
    comic = models.ForeignKey(Comic, on_delete=models.PROTECT)
    slug = models.CharField(max_length=32)
    title = models.CharField(max_length=128)
    ordering = models.FloatField()
    post = models.TextField(blank=True)
    transcript = models.TextField(blank=True)
    image = models.ImageField()
    alt_text = models.CharField(max_length=150, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)

    class Meta:
        unique_together = (("comic", "slug"), ("comic", "ordering"), )

    def __str__(self):
        return f'{self.comic} - {self.title}'
