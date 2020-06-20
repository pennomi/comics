import itertools
import re

from django.db.models import Q
from django.urls import reverse
from markdown2 import Markdown


TAG_REFERENCE_RE = re.compile(r"<([\w\- ]+):([\w\- ]+)>", re.I)


def grouper(iterable, n):
    """
    Collect data into fixed-length chunks or blocks.
    See https://docs.python.org/3.3/library/itertools.html?highlight=zip#itertools-recipes
    """
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=None)


class BetterMarkdown(Markdown):
    def _add_tags(self):
        pass

    def preprocess(self, text):
        parts = list(TAG_REFERENCE_RE.split(text))

        # Run over the objects once to build the query
        query = Q()
        for markdown_chunk, tag_type, tag in grouper(parts, 3):
            if tag_type and tag:
                query |= Q(type__title__iexact=tag_type, title__iexact=tag)

        # Fetch the requested tags from the DB

        from apps.comics.models import Tag
        tag_objects = Tag.objects.filter(query).select_related("type")
        tags_and_icons = {(t.type.title.lower(), t.title.lower()): t.icon_url for t in tag_objects}

        # Iterate over the objects again to replace the areas with the correct markup
        new_text = ""
        for markdown_chunk, tag_type, tag in grouper(parts, 3):
            tag_type = tag_type.lower() if tag_type else None
            tag = tag.lower() if tag else None
            if not tag_type or not tag:
                tag_html = ""
            elif (tag_type, tag) in tags_and_icons:
                url = reverse("archive-tag", kwargs={"type": tag_type, "tag": tag})
                tag_html = f'<a style="background-image: url({tags_and_icons[(tag_type, tag)]});" class="tag" href="{url}">{tag}</a>'
            else:
                tag_html = f'<a class="tag error" href="">{tag}</a>'
            new_text += f'{markdown_chunk}{tag_html}'
        return new_text

    def postprocess(self, text):
        return text


MARKDOWN_ENGINE = BetterMarkdown()


def render(text) -> str:
    """Render an HTML version of the text."""
    return MARKDOWN_ENGINE.convert(text)


def render_txt(text) -> str:
    """Render a plaintext version of the text. This is naive and should be made more robust, but it works for now."""
    text = TAG_REFERENCE_RE.sub(r"[\2]", text)
    text = text.replace("\r\n", "\n")
    text = text.replace(">", "")
    text = text.replace("[", "")
    text = text.replace("]", "")
    text = text.replace("*", "")
    text = text.replace("\n ", "\n")
    text = text.replace("\n\n", "\n")
    return text
