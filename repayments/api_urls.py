from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import RepaymentViewSet

router = DefaultRouter()
router.register('', RepaymentViewSet, basename='repayment')

urlpatterns = [
    path('', include(router.urls)),
]
