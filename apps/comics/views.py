import itertools
import json

from django.conf import settings
from django.db.models import Count
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template.defaultfilters import date
from django.urls import reverse
from django.utils.timezone import now
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView, RedirectView
from django.utils.decorators import method_decorator

from apps.comics.models import Comic, Page, TagType, Tag, Ad


def require_comic(cls):
    """A View class decorator that redirects the page to the comics index if no comic is found."""
    def outside(func):
        def wrapper(self, *args, **kwargs):
            if self.request.comic is None:
                return HttpResponseRedirect(reverse("index"))
            return func(self, *args, **kwargs)
        return wrapper
    cls.get = outside(cls.get)
    return cls


class Redirect(Exception):
    def __init__(self, url):
        self.url = url


def handle_redirect_exception(cls):
    """A View class decorator that redirects the page to the comics index if no comic is found."""
    def outside(func):
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Redirect as e:
                return HttpResponseRedirect(e.url)
        return wrapper
    cls.get = outside(cls.get)
    return cls


class ComicsIndexView(View):
    """This view redirects the user to the latest comic if we're on a configured domain, otherwise it goes to a
    list page that shows what comics are available.
    """
    def get(self, request):
        # If we are on a domain that has a comic configured, take us to the reader
        if request.comic:
            return HttpResponseRedirect(reverse("reader-redirect"))
        # If we are on any other domain, instead show the index.
        return render(request, 'comics/index.html', {'comics': Comic.objects.all()})


@require_comic
class ReaderRedirectView(RedirectView):
    """ If the user comes to visit the site without a specific page, redirect
    that user to the most recent comic available.
    """
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        comic = self.request.comic
        page = comic.pages.active().order_by('-ordering').first()
        if page is None:
            # But if there's no page, take us to the admin, I guess. TODO: Have a "no content" template
            return reverse("admin:index")
        return self.request.build_absolute_uri(page.get_absolute_url())


@require_comic
class RandomReaderRedirectView(RedirectView):
    """ If the user comes to this page, redirect that user to a random published comic.
    """
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        comic = self.request.comic
        page = comic.pages.active().order_by('?').first()
        if page is None:
            # But if there's no page, take us to the admin, I guess. TODO: Have a "no content" template
            return reverse("admin:index")
        return self.request.build_absolute_uri(page.get_absolute_url())

    def dispatch(self, *args, **kwargs):
        response = super().dispatch(*args, **kwargs)
        response['Cache-Control'] = "max-age=600"  # 10 minutes
        return response


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


@handle_redirect_exception
@require_comic
class ReaderView(TemplateView):
    template_name = "comics/reader.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comic = self.request.comic
        page = get_object_or_404(Page, comic=comic, slug__iexact=kwargs['page'])
        if page.posted_at > now():
            raise Http404()
        # If we have an improper capitalization of the slug, instead redirect to the canonical capitalization
        if page.slug != kwargs['page']:
            raise Redirect(reverse('reader', kwargs={'page': page.slug}))

        context['comic'] = comic
        context['page'] = page
        context['nav'] = _get_navigation_pages(page)
        context['ad'] = Ad.objects.filter(type="Banner").active(comic)
        context['dialog_ad'] = Ad.objects.filter(type="Popup").active(comic)
        return context


class FeedView(TemplateView):
    template_name = "comics/rss.xml"

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        response['Content-Type'] = 'application/xml'
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comic = self.request.comic
        context['comic'] = comic
        context['pages'] = comic.pages.active().order_by('-ordering')[:10]
        context['feed_url'] = reverse('feed')
        return context


@method_decorator(cache_page(60 * 60), name='dispatch')
@handle_redirect_exception
class ComicAjaxView(View):
    def get(self, request, *args, **kwargs):
        comic = request.comic

        # Build the json
        data = json.dumps({
            "socialLinks": [{
                "title": s.title or s.platform.name,
                "image": s.platform.image.url if s.platform.image else "",
                "visitUrl": s.visit_url,
                "followUrl": s.follow_url or s.visit_url,
                "shareUrlTemplate": s.platform.share_template,
                "visitCta": s.visit_cta or s.platform.visit_cta,
                "followCta": s.follow_cta or s.platform.follow_cta,
                "shareCta": s.share_cta or s.platform.share_cta,
                "requiresMoney": s.platform.requires_money,
            } for s in comic.social_links.all()],
            "pages": [p.slug for p in comic.pages.active()],
        })

        response = HttpResponse(data)
        response["Content-Type"] = "application/json"
        return response


@method_decorator(cache_page(60 * 60), name='dispatch')
@handle_redirect_exception
class PageAjaxView(View):
    def get(self, request, *args, **kwargs):
        comic = request.comic
        page = get_object_or_404(Page, comic=comic, slug=kwargs['page'])
        if page.posted_at > now():
            raise Http404()
        # If we have an improper capitalization of the slug, instead redirect to the canonical capitalization
        if page.slug != kwargs['page']:
            raise Redirect(reverse('reader', kwargs={'page': page.slug}))

        pages = _get_navigation_pages(page)

        # Compute tag data
        tags = page.tags.order_by('type__title', 'title')
        tag_types = itertools.groupby(tags, lambda _: _.type)
        tag_type_data = [{"title": key.title, "tags": [{
            "url": reverse("archive-tag", kwargs={"type": t.type.title, "tag": t.title}),
            "title": t.title,
            "icon": t.icon_url if t.icon_url else ""
        } for t in value]} for key, value in tag_types]

        # Build the json
        data = json.dumps({
            "slug": page.slug,
            "title": page.title,
            "post": page.post_html,
            "posted_at": date(page.posted_at),
            "transcript": page.transcript_html,
            "image": page.image.url,
            "alt_text": page.alt_text,
            "tag_types": tag_type_data,

            # Get the comic list
            "first": pages['first'].slug if pages['first'] else None,
            "previous": pages['previous'].slug if pages['previous'] else None,
            "next": pages['next'].slug if pages['next'] else None,
            "last": pages['last'].slug if pages['last'] else None,

            # Admin edit link for those who have access
            "admin": reverse("admin:comics_page_change", args=[page.id]),
        })

        response = HttpResponse(data)
        response["Content-Type"] = "application/json"
        return response


@require_comic
class TestView(ReaderView):
    def get_context_data(self, **kwargs):
        comic = self.request.comic
        page = comic.pages.active().order_by('-ordering').first()
        kwargs['page'] = page.slug
        context = super().get_context_data(**kwargs)
        context['testing'] = True
        return context


@require_comic
class ArchiveView(TemplateView):
    template_name = "comics/archive/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comic = self.request.comic
        context['comic'] = comic
        context['ad'] = Ad.objects.filter(type="Banner").active(comic)
        context['dialog_ad'] = Ad.objects.filter(type="Popup").active(comic)
        return context


@require_comic
class CommunityView(TemplateView):
    template_name = "comics/community.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comic = self.request.comic
        context['comic'] = comic
        return context


@require_comic
class PageListView(TemplateView):
    template_name = "comics/archive/pages.html"

    def get_context_data(self, **kwargs):
        comic = self.request.comic
        pages = comic.pages.active()
        chapters = comic.chapters.all()
        pages_and_chapters = list(pages) + list(chapters)
        pages_and_chapters.sort(key=lambda x: x.ordering)

        context = super().get_context_data(**kwargs)
        context['comic'] = comic
        context['pages_and_chapters'] = pages_and_chapters
        context['breadcrumbs'] = [
            {'title': 'Archive', 'url': reverse('archive-index'),
             'icon': comic.archive_icon.url if comic.archive_icon else None},
        ]
        context['ad'] = Ad.objects.filter(type="Banner").active(comic)
        context['dialog_ad'] = Ad.objects.filter(type="Popup").active(comic)
        return context


@handle_redirect_exception
@require_comic
class TagTypeView(TemplateView):
    template_name = "comics/archive/tagtype.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comic = self.request.comic
        tag_type = get_object_or_404(TagType, comic=comic, title__iexact=kwargs['type'])

        # If we have an improper capitalization of the tag, instead redirect to the canonical capitalization
        if tag_type.title != kwargs['type']:
            raise Redirect(reverse('archive-tagtype', kwargs={'type': tag_type.title}))

        context['comic'] = comic
        context['tag_type'] = tag_type
        context['sorted_tags'] = tag_type.tags.annotate(count=Count('pages')).order_by('-count')
        context['breadcrumbs'] = [
            {'title': 'Archive', 'url': reverse('archive-index'),
             'icon': comic.archive_icon.url if comic.archive_icon else None},
        ]
        context['ad'] = tag_type.ad_override if tag_type.ad_override else Ad.objects.filter(type="Banner").active(comic)
        context['dialog_ad'] = Ad.objects.filter(type="Popup").active(comic)
        return context


@handle_redirect_exception
@require_comic
class TagView(TemplateView):
    template_name = "comics/archive/tag.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comic = self.request.comic
        tag_type = get_object_or_404(TagType, comic=comic, title__iexact=kwargs['type'])
        tag = get_object_or_404(Tag, type=tag_type, title__iexact=kwargs['tag'])

        # If we have an improper capitalization of the tag, instead redirect to the canonical capitalization
        if tag_type.title != kwargs['type'] or tag.title != kwargs['tag']:
            raise Redirect(reverse('archive-tag', kwargs={'type': tag_type.title, 'tag': tag.title}))

        context['comic'] = comic
        context['tag_type'] = tag_type
        context['tag'] = tag
        context['breadcrumbs'] = [
            {'title': 'Archive', 'url': reverse('archive-index'),
             'icon': comic.archive_icon.url if comic.archive_icon else None},
            {'title': tag_type.title,
             'url': reverse('archive-tagtype', kwargs={'type': tag_type.title}),
             'icon': tag_type.best_icon},
        ]
        context['ad'] = tag.ad_override if tag.ad_override else Ad.objects.filter(type="Banner").active(comic)
        context['dialog_ad'] = Ad.objects.filter(type="Popup").active(comic)
        return context


class AdsTxt(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        if settings.ADS_TXT_URL is None:
            raise Http404()
        return settings.ADS_TXT_URL


class LegacyPageRedirectView(RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        url = self.request.build_absolute_uri()
        url = url.replace("/swords/", "/comic/")
        return url


def comic_404_view(request, exception):
    return render(request, "comics/404.html", {'comic': request.comic})


def comic_500_view(request):
    return render(request, "comics/500.html", {'comic': request.comic})


class Test500View(View):
    def get(self, request, *args, **kwargs):
        raise Exception("Ouch")


class SitemapView(View):
    def get(self, request, *args, **kwargs):
        pass


class RobotsTxtView(View):
    def get(self, request, *args, **kwargs):
        data = f"""User-agent: *
Disallow: 
Sitemap: {reverse('sitemap')}
        """
        return HttpResponse(data)
