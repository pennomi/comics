"""comics URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static

from apps.comics import views as comics_views

urlpatterns = [
    path('', comics_views.ComicsIndexView.as_view(), name='index'),
    path('admin/', admin.site.urls),

    # Comic root
    path('<slug:comic>/', comics_views.ReaderRedirectView.as_view(), name='reader-redirect'),

    # Special pages  # TODO: Make these illegal slugs for pages
    path('<slug:comic>/archive/', comics_views.ArchiveView.as_view(), name='archive'),
    path('<slug:comic>/feed/', comics_views.FeedView.as_view(), name='feed'),

    # Individual pages
    path('<slug:comic>/<slug:page>/', comics_views.ReaderView.as_view(), name='reader'),
    path('<slug:comic>/data/<slug:page>/', comics_views.PageAjaxView.as_view(), name='page'),

    # Tag Wiki Pages
    path('<slug:comic>/tag/<str:type>/', comics_views.TagTypeView.as_view(), name='tagtype'),
    path('<slug:comic>/tag/<str:type>/<str:tag>/', comics_views.TagView.as_view(), name='tag'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
