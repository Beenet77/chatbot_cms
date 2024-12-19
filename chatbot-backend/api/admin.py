from django.contrib import admin
from .models import CMSContent, ChatMessage
from .models import Logo,Copyright
from django.utils.html import format_html

@admin.register(CMSContent)
class CMSContentAdmin(admin.ModelAdmin):
    list_display = ('key', 'query', 'updated_at')
    list_filter = ('query', )
    search_fields = ('key', 'content')
    ordering = ('key', 'query')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Content Information', {
            'fields': ('key', 'query')
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



class LogoAdmin(admin.ModelAdmin):
    list_display = ('id', 'logo_image','logo_type')
    fields = ('logo','logo_type')
    def logo_image(self, obj):
        if obj.logo:  # Check if the object has a logo
            return format_html(f'<img src="{obj.logo.url}" width="100" height="100" style="object-fit:contain;" />', )
        return "No Image"


    logo_image.short_description = 'Logo Image'

    def has_add_permission(self, request):
        if Logo.objects.count() >= 2:  
            return False
        return True

admin.site.register(Logo, LogoAdmin)

class CopyrightAdmin(admin.ModelAdmin):
    
    list_display = ('id', 'content')
    fields = ('content',)  
    def has_add_permission(self, request):
        if Copyright.objects.count() >= 1: 
            return False
        return True

admin.site.register(Copyright, CopyrightAdmin)
