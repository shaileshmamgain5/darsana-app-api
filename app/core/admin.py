"""
Django admin customizations.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core import models


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            _('Permissions'),
            {'fields': (
                'is_active',
                'is_staff',
                'is_superuser'
            )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)})
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser',
            )
        }),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Thread)
admin.site.register(models.ChatSession)
admin.site.register(models.ChatMessage)
admin.site.register(models.Tag)
admin.site.register(models.UserSubscription)
admin.site.register(models.Category)
admin.site.register(models.Profile)
admin.site.register(models.AppConfiguration)
admin.site.register(models.MoodEntry)
admin.site.register(models.MoodTag)
admin.site.register(models.MoodResponse)
admin.site.register(models.ModelConfiguration)
admin.site.register(models.PerformanceMetric)


class JournalTemplateAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_user_email', 'visibility', 'is_system_created', 'created_at']
    list_filter = ['visibility', 'is_system_created', 'user']
    search_fields = ['title', 'user__email']

    def get_user_email(self, obj):
        return obj.user.email if obj.user else 'System'
    get_user_email.short_description = 'User Email'

admin.site.register(models.JournalTemplate, JournalTemplateAdmin)


class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['get_user_email', 'get_journal_template_title', 'get_standalone_prompt_title', 'is_completed', 'created_at']
    list_filter = ['is_completed', 'user', 'journal_template', 'standalone_prompt']
    search_fields = ['user__email', 'journal_template__title', 'standalone_prompt__title']

    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'User Email'

    def get_journal_template_title(self, obj):
        return obj.journal_template.title if obj.journal_template else 'N/A'
    get_journal_template_title.short_description = 'Journal Template'

    def get_standalone_prompt_title(self, obj):
        return obj.standalone_prompt.title if obj.standalone_prompt else 'N/A'
    get_standalone_prompt_title.short_description = 'Standalone Prompt'

admin.site.register(models.JournalEntry, JournalEntryAdmin)

class JournalTopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_journal_template_title']
    list_filter = ['journal']
    search_fields = ['title', 'journal__title']

    def get_journal_template_title(self, obj):
        return obj.journal.title
    get_journal_template_title.short_description = 'Journal Template'

admin.site.register(models.JournalTopic, JournalTopicAdmin)

class StandalonePromptAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_user_email', 'visibility', 'is_system_created', 'created_at']
    list_filter = ['visibility', 'is_system_created', 'user']
    search_fields = ['title', 'user__email']

    def get_user_email(self, obj):
        return obj.user.email if obj.user else 'System'
    get_user_email.short_description = 'User Email'

admin.site.register(models.StandalonePrompt, StandalonePromptAdmin)

class JournalPromptAdmin(admin.ModelAdmin):
    list_display = ['get_prompt_text', 'get_topic_title', 'get_journal_template_title', 'is_answer_required', 'order']
    list_filter = ['is_answer_required', 'topic__journal']
    search_fields = ['prompt_text', 'topic__title', 'topic__journal__title']

    def get_prompt_text(self, obj):
        return obj.prompt_text[:50] + '...' if len(obj.prompt_text) > 50 else obj.prompt_text
    get_prompt_text.short_description = 'Prompt Text'

    def get_topic_title(self, obj):
        return obj.topic.title if obj.topic else 'N/A'
    get_topic_title.short_description = 'Topic'

    def get_journal_template_title(self, obj):
        return obj.topic.journal.title if obj.topic and obj.topic.journal else 'N/A'
    get_journal_template_title.short_description = 'Journal Template'

admin.site.register(models.JournalPrompt, JournalPromptAdmin)

class PromptEntryAdmin(admin.ModelAdmin):
    list_display = ['get_user_email', 'get_journal_entry_id', 'get_prompt_text', 'get_response_preview', 'created_at']
    list_filter = ['journal_entry__user', 'created_at']
    search_fields = ['journal_entry__user__email', 'user_prompt_text', 'user_response_text']

    def get_user_email(self, obj):
        return obj.journal_entry.user.email
    get_user_email.short_description = 'User Email'

    def get_journal_entry_id(self, obj):
        return obj.journal_entry.id
    get_journal_entry_id.short_description = 'Journal Entry ID'

    def get_prompt_text(self, obj):
        prompt_text = obj.user_prompt_text
        if isinstance(prompt_text, list):
            prompt_text = ' '.join(prompt_text)
        return (prompt_text[:50] + '...') if len(prompt_text) > 50 else prompt_text
    get_prompt_text.short_description = 'Prompt Text'

    def get_response_preview(self, obj):
        response_text = obj.user_response_text
        if isinstance(response_text, list):
            response_text = ' '.join(response_text)
        return (response_text[:50] + '...') if len(response_text) > 50 else response_text
    get_response_preview.short_description = 'Response Preview'

admin.site.register(models.PromptEntry, PromptEntryAdmin)
