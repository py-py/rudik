from rest_framework import routers

from .endpoints.order import OrderViewSet

router = routers.DefaultRouter()
router.register("order", OrderViewSet)

urlpatterns = router.urls
