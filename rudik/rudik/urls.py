from django.urls import path

from .admin import rudik_site

urlpatterns = [path("admin/", rudik_site.urls)]
