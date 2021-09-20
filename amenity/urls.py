from rest_framework.routers import DefaultRouter

from .views import AmenityViewSet

router = DefaultRouter()
router.register(prefix='', viewset=AmenityViewSet, basename='amenity')

urlpatterns = router.urls
