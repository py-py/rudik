from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .admin import rudik_site

urlpatterns = [path("admin/", rudik_site.urls)] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)
