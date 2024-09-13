from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StandalonePromptViewSet

router = DefaultRouter()
router.register(r'standalone-prompts', StandalonePromptViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
