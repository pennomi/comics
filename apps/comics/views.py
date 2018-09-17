import itertools
import json

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import date
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView, RedirectView

from apps.comics.models import Comic, Page, TagType, Tag


class ComicsIndexView(TemplateView):
    template_name = "comics/index.html"


class ReaderRedirectView(RedirectView):
    """ If the user comes to visit the site without a specific page, redirect
    that user to the most recent comic available.
    """
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        comic = get_object_or_404(Comic, slug=kwargs['comic'])
        page = comic.pages.order_by('-ordering').first()
        return reverse("reader", kwargs={
            "comic": kwargs['comic'],
            "page": page.slug,
        })


class ReaderView(TemplateView):
    template_name = "comics/reader.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        comic = get_object_or_404(Comic, slug=kwargs['comic'])
        page = get_object_or_404(Page, comic=comic, slug=kwargs['page'])
        context['comic'] = comic
        context['page'] = page
        return context


class PageAjaxView(View):
    def get(self, request, *args, **kwargs):
        comic = get_object_or_404(Comic, slug=kwargs['comic'])
        page = get_object_or_404(Page, comic=comic, slug=kwargs['page'])

        first_page = comic.pages.order_by('ordering').first()
        prev_page = comic.pages.filter(
            ordering__lt=page.ordering
        ).order_by('-ordering').first()
        next_page = comic.pages.filter(
            ordering__gt=page.ordering
        ).order_by('ordering').first()
        last_page = comic.pages.order_by('-ordering').first()

        # Compute tag data
        tags = page.tags.order_by('type__title', 'title')
        tag_types = itertools.groupby(tags, lambda _: _.type)
        tag_type_data = [{"title": key.title, "tags": [{
            "url": reverse("tag", kwargs={"comic": comic.slug, "type": t.type.title, "tag": t.title}),
            "title": t.title,
            "icon": t.icon.url if t.icon else ""
        } for t in value]} for key, value in tag_types]

        # Build the json
        data = json.dumps({
            "slug": page.slug,
            "title": page.title,
            "post": page.post,
            "posted_at": date(page.posted_at),
            "transcript": page.transcript,
            "image": page.image.url,
            "alt_text": page.alt_text,
            "tag_types": tag_type_data,

            # Get the comic list
            "first": first_page.slug if first_page else None,
            "previous": prev_page.slug if prev_page else None,
            "next": next_page.slug if next_page else None,
            "last": last_page.slug if last_page else None,

            # Optional Admin edit link
            "admin": reverse("admin:comics_page_change", args=[page.id]) if request.user.is_staff else None,
        })

        response = HttpResponse(data)
        response["Content-Type"] = "application/json"
        return response


class ArchiveView(TemplateView):
    template_name = "comics/archive.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comic = get_object_or_404(Comic, slug=kwargs['comic'])
        context['comic'] = comic
        return context


class TagTypeView(TemplateView):
    template_name = "comics/tagtype.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comic = get_object_or_404(Comic, slug=kwargs['comic'])
        tag_type = get_object_or_404(TagType, comic=comic, title=kwargs['type'])
        context['comic'] = comic
        context['tag_type'] = tag_type
        return context


class TagView(TemplateView):
    template_name = "comics/tag.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comic = get_object_or_404(Comic, slug=kwargs['comic'])
        tag_type = get_object_or_404(TagType, comic=comic, title=kwargs['type'])
        tag = get_object_or_404(Tag, type=tag_type, title=kwargs['tag'])
        context['comic'] = comic
        context['tag_type'] = tag_type
        context['tag'] = tag
        return context
