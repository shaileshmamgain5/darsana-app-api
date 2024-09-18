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
admin.site.register(models.StandalonePrompt)
admin.site.register(models.JournalTemplate)
admin.site.register(models.JournalTopic)
admin.site.register(models.JournalPrompt)
admin.site.register(models.JournalEntry)
admin.site.register(models.PromptEntry)
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
