from django.db import models
from django.conf import settings
import os
import shutil

LOGO_CHOICE=(
    ("chatbot","Chatbot Logo"),
    ("main","Main Logo"),    
)

class CMSContent(models.Model):
    key = models.CharField(max_length=100)
    content = models.TextField()
    language = models.CharField(
        max_length=10, 
        choices=[('en', 'English'), ('ne', 'Nepali')],
        default='en'
    )
    query = models.CharField(max_length=250)
    keywords = models.TextField(blank=True, help_text="Comma-separated keywords")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('key', 'language')
        indexes = [
            models.Index(fields=['query']),
            models.Index(fields=['language']),
            models.Index(fields=['keywords']),
        ]

    def save(self, *args, **kwargs):
        # Convert query to lowercase before saving
        self.query = self.query.lower()
        
        # Generate keywords if not provided
        if not self.keywords:
            # Extract unique words from both query and content
            query_words = set(self.query.lower().split())
            content_words = set(self.content.lower().split())
            # Combine unique words, excluding common words
            common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            all_words = (query_words.union(content_words)) - common_words
            self.keywords = ','.join(all_words)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.key} ({self.language})"

class ChatMessage(models.Model):
    user_message = models.TextField()
    bot_response = models.TextField()
    language = models.CharField(max_length=10, default='en')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message at {self.timestamp}"
class Logo(models.Model):
    logo = models.ImageField(upload_to='logos/', verbose_name="Logo Image")
    logo_type= models.CharField(choices=LOGO_CHOICE,max_length=30,default="main")

    class Meta:
        verbose_name = "Logo"
        verbose_name_plural = "Logos"
        ordering = ['-id']

    def __str__(self):
        return f"Logo ID: {self.id} "
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save the object first

        # Check if logo_type is "main" and the logo file exists
        if self.logo_type == "main" and self.logo:
            # Ensure STATIC_URL is configured
            static_logo_path = os.path.join(settings.BASE_DIR, 'static', 'logos')
            
            # Ensure the static directory exists
            os.makedirs(static_logo_path, exist_ok=True)

            # Define the new file name as 'logo'
            new_logo_name = 'logo' + os.path.splitext(self.logo.name)[-1]  # Keep the same extension

            # Check if there is an existing 'logo' in the static directory
            existing_logo_path = os.path.join(static_logo_path, 'logo' + os.path.splitext(self.logo.name)[-1])
            if os.path.exists(existing_logo_path):
                os.remove(existing_logo_path)  # Remove the existing logo

            # Copy the new logo file to the static directory
            logo_path = self.logo.path  # Get the full path of the uploaded logo
            if os.path.exists(logo_path):  # Ensure the logo file exists
                destination_path = os.path.join(static_logo_path, new_logo_name)
                shutil.copy(logo_path, destination_path)
  
class Copyright(models.Model):
    
    content= models.CharField(max_length=30)

    class Meta:
        verbose_name = "Copyright"
        verbose_name_plural = "Copyrights"
       

    def __str__(self):
        return f"Copyright ID: {self.id} "
  

