from rest_framework import routers

from .endpoints import CategoryViewSet
from .endpoints import ProductViewSet

router = routers.DefaultRouter()
router.register("product", ProductViewSet)
router.register("category", CategoryViewSet)

urlpatterns = router.urls
