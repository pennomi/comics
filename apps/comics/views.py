import itertools
import json

from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import date
from django.urls import reverse
from django.utils.timezone import now
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView, RedirectView
from django.utils.decorators import method_decorator


from apps.comics.models import Comic, Page, TagType, Tag, Ad


class ComicsIndexView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        page = Page.objects.order_by('-ordering').first()
        if page is None:
            return reverse("admin:index")
        return reverse("reader", kwargs={"comic": page.comic.slug, "page": page.slug})


class ReaderRedirectView(RedirectView):
    """ If the user comes to visit the site without a specific page, redirect
    that user to the most recent comic available.
    """
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        comic = get_object_or_404(Comic, slug=kwargs['comic'])
        page = comic.pages.active().order_by('-ordering').first()
        return self.request.build_absolute_uri(page.get_absolute_url())


def _get_navigation_pages(current_page):
    comic = current_page.comic
    return {
        "first": comic.pages.active().order_by('ordering').first(),
        "previous": comic.pages.active().filter(
            ordering__lt=current_page.ordering
        ).order_by('-ordering').first(),
        "next": comic.pages.active().filter(
            ordering__gt=current_page.ordering
        ).order_by('ordering').first(),
        "last": comic.pages.active().order_by('-ordering').first(),
    }


class ReaderView(TemplateView):
    template_name = "comics/reader.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comic = get_object_or_404(Comic, slug=kwargs['comic'])
        page = get_object_or_404(Page, comic=comic, slug=kwargs['page'])
        if page.posted_at > now():
            raise Http404()
        context['comic'] = comic
        context['page'] = page
        context['nav'] = _get_navigation_pages(page)
        context['ad'] = Ad.objects.filter(comic=comic, active=True).order_by("?").first()
        return context


class FeedView(TemplateView):
    template_name = "comics/rss.xml"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comic = get_object_or_404(Comic, slug=kwargs['comic'])
        context['comic'] = comic
        context['pages'] = comic.pages.active().order_by('-ordering')[:10]
        return context


@method_decorator(cache_page(60 * 60), name='dispatch')
class PageAjaxView(View):
    def get(self, request, *args, **kwargs):
        comic = get_object_or_404(Comic, slug=kwargs['comic'])
        page = get_object_or_404(Page, comic=comic, slug=kwargs['page'])
        if page.posted_at > now():
            raise Http404()

        pages = _get_navigation_pages(page)

        # Compute tag data
        tags = page.tags.order_by('type__title', 'title')
        tag_types = itertools.groupby(tags, lambda _: _.type)
        tag_type_data = [{"title": key.title, "tags": [{
            "url": reverse("tag", kwargs={"comic": comic.slug, "type": t.type.title, "tag": t.title}),
            "title": t.title,
            "icon": t.icon_url if t.icon_url else ""
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
            "first": pages['first'].slug if pages['first'] else None,
            "previous": pages['previous'].slug if pages['previous'] else None,
            "next": pages['next'].slug if pages['next'] else None,
            "last": pages['last'].slug if pages['last'] else None,

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
