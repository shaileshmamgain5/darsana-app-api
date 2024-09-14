from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MoodEntryViewSet, MoodTagViewSet

router = DefaultRouter()
router.register(r'entries', MoodEntryViewSet, basename='mood-entry')
router.register(r'tags', MoodTagViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
