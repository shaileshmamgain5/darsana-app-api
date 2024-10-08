from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JournalTemplateViewSet, JournalTopicViewSet, JournalPromptViewSet, JournalEntryViewSet, PromptEntryViewSet

router = DefaultRouter()
router.register(r'templates', JournalTemplateViewSet)
#router.register(r'topics', JournalTopicViewSet)
#router.register(r'prompts', JournalPromptViewSet)
router.register(r'entries', JournalEntryViewSet, basename='journal-entry')
router.register(r'prompt-entries', PromptEntryViewSet, basename='prompt-entry')

urlpatterns = [
    path('', include(router.urls)),
]