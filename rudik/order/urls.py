from rest_framework import routers

from .endpoints.delivery import DeliveryViewSet
from .endpoints.order import OrderViewSet

router = routers.DefaultRouter()
router.register("order", OrderViewSet)
router.register("delivery", DeliveryViewSet, basename="delivery")
urlpatterns = router.urls
