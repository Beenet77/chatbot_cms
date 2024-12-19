from django.contrib import admin
from .models import CMSContent, ChatMessage
from .models import Logo
from django.utils.html import format_html

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
class LogoAdmin(admin.ModelAdmin):
    # Display 'id' and the custom 'logo_image' method in the table (list view)
    list_display = ('id', 'logo_image','logo_type')
    fields = ('logo','logo_type')  # Specify the fields to be shown in the edit form

    # Custom method to render the logo image in the admin panel
    def logo_image(self, obj):
        """
        Display the logo image in the admin list view.
        """
        if obj.logo:  # Check if the object has a logo
            return format_html(f'<img src="{obj.logo.url}" width="100" height="100" style="object-fit:contain;" />', )
        return "No Image"

    # Short description for the column in the admin panel
    logo_image.short_description = 'Logo Image'

    # Restrict adding more than one logo
    def has_add_permission(self, request):
        if Logo.objects.count() >= 2:  # Only one logo can be added
            return False
        return True

# Register the Logo model with its custom admin
admin.site.register(Logo, LogoAdmin)
