from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TagViewSet, CategoryViewSet, JournalTemplateViewSet, JournalTopicViewSet,
    JournalPromptViewSet, StandalonePromptViewSet, JournalEntryViewSet,
    PromptEntryViewSet, QuoteViewSet, JournalSummaryViewSet
)

router = DefaultRouter()
router.register(r'tags', TagViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'journal-templates', JournalTemplateViewSet)
router.register(r'journal-topics', JournalTopicViewSet)
router.register(r'journal-prompts', JournalPromptViewSet)
router.register(r'standalone-prompts', StandalonePromptViewSet)
router.register(r'journal-entries', JournalEntryViewSet)
router.register(r'prompt-entries', PromptEntryViewSet)
router.register(r'quotes', QuoteViewSet)
router.register(r'journal-summaries', JournalSummaryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
