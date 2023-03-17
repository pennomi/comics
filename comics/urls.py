from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls.static import static

from apps.comics import views as comics_views


urlpatterns = [
    path('', comics_views.ComicsIndexView.as_view(), name='index'),
    path('admin/', admin.site.urls),
    path('ads.txt', comics_views.AdsTxt.as_view(), name='ads-txt'),
    # path('robots.txt', comics_views.RobotsTxtView.as_view(), name='robots'),
    # path('sitemap.xml', comics_views.SitemapView.as_view(), name='sitemap'),

    # Comic root
    path('', comics_views.ReaderRedirectView.as_view(), name='reader-redirect'),
    path('comic/', comics_views.ReaderRedirectView.as_view(), name='reader-redirect'),
    path('comic/random/', comics_views.RandomReaderRedirectView.as_view(), name='random-reader-redirect'),

    # Legacy redirects
    re_path(r'^swords/', comics_views.LegacyPageRedirectView.as_view(), name='legacy-page-redirect'),

    # Reader
    path('comic/feed/', comics_views.FeedView.as_view(), name='feed'),  # RSS Feed
    path('comic/rss.xml', comics_views.FeedView.as_view(), name='feed'),  # RSS Feed Alternate URL
    path('comic/data/', comics_views.ComicAjaxView.as_view(), name='comic-metadata'),
    path('comic/data/<slug:page>/', comics_views.PageAjaxView.as_view(), name='page-metadata'),
    path('comic/<slug:page>/', comics_views.ReaderView.as_view(), name='reader'),

    # Testing
    path('test/', comics_views.TestView.as_view(), name='test'),

    # Tag Wiki Pages
    path('archive/', comics_views.ArchiveView.as_view(), name='archive-index'),
    path('archive/pages/', comics_views.PageListView.as_view(), name='archive-pages'),
    path('archive/<str:type>/', comics_views.TagTypeView.as_view(), name='archive-tagtype'),
    path('archive/<str:type>/<str:tag>/', comics_views.TagView.as_view(), name='archive-tag'),

    # Miscellaneous
    path('community/', comics_views.CommunityView.as_view(), name='community'),
    path('500/', comics_views.comic_500_view),
    path('<str:short_code>', comics_views.ShortCodeRedirectView.as_view(), name = 'configured-redirect'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = comics_views.comic_404_view
handler500 = comics_views.comic_500_view
