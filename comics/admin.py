"""Configure a custom admin page that sets a browser cookie signalling login for editors"""
from django.contrib import admin
from django.contrib.admin import apps


class ComicsAdminSite(admin.AdminSite):
    index_template = 'admin/admin_index_template.html'


class ComicsAdminConfig(apps.AdminConfig):
    default_site = 'comics.admin.ComicsAdminSite'

