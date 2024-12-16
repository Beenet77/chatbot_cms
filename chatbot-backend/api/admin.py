from django.contrib import admin
from .models import CMSContent, ChatMessage

@admin.register(CMSContent)
class CMSContentAdmin(admin.ModelAdmin):
    list_display = ('key', 'language', 'category', 'updated_at')
    list_filter = ('language', 'category')
    search_fields = ('key', 'content')
    ordering = ('key', 'language')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Content Information', {
            'fields': ('key', 'language', 'category')
        }),
        ('Content', {
            'fields': ('content',),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user_message', 'bot_response', 'language', 'timestamp')
    list_filter = ('language', 'timestamp')
    search_fields = ('user_message', 'bot_response')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)

    def has_add_permission(self, request):
        return False  # Prevent adding chat messages manually

    def has_change_permission(self, request, obj=None):
        return False  # Prevent editing chat messages


# Register your models here.
