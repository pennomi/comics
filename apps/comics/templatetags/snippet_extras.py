from django import template
from django.utils.safestring import mark_safe

from apps.comics.models import CodeSnippet

register = template.Library()


def _snippet_base(context, location):
    comic = context["request"].comic
    test_mode = context.get("testing", False)
    snips = CodeSnippet.objects.for_comic(comic).filter(testing=test_mode)
    snippet_string = "\n".join(s.code for s in snips.filter(location=location))
    return mark_safe(snippet_string)


@register.simple_tag(takes_context=True)
def snippets_start_of_head(context):
    return _snippet_base(context, 0)


@register.simple_tag(takes_context=True)
def snippets_end_of_body(context):
    return _snippet_base(context, 1)


@register.simple_tag(takes_context=True)
def snippets_ad_header(context):
    return _snippet_base(context, 2)


@register.simple_tag(takes_context=True)
def snippets_ad_content(context):
    return _snippet_base(context, 3)


@register.simple_tag(takes_context=True)
def snippets_ad_info(context):
    return _snippet_base(context, 4)
