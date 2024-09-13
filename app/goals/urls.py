from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GoalViewSet

router = DefaultRouter()
router.register(r'goals', GoalViewSet, basename='goal')

urlpatterns = [
    path('', include(router.urls)),
]
