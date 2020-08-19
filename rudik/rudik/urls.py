from django.conf import settings
from django.conf.urls.static import static
from django.urls import include
from django.urls import path

from .admin import rudik_site

api_urlpatterns = [
    path("product/", include("product.urls")),
]

urlpatterns = [
    path("admin/", rudik_site.urls),
    path("api/v1/", include(api_urlpatterns)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
