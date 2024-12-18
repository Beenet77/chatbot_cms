from django.db import models

class CMSContent(models.Model):
    key = models.CharField(max_length=100)
    content = models.TextField()
    language = models.CharField(max_length=10, choices=[
        ('en', 'English'),
        ('ne', 'Nepali')
    ])
    category = models.CharField(max_length=50, default='general')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('key', 'language')

class ChatMessage(models.Model):
    user_message = models.TextField()
    bot_response = models.TextField()
    language = models.CharField(max_length=10, default='en')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message at {self.timestamp}"
class Logo(models.Model):
    logo = models.ImageField(upload_to='logos/', verbose_name="Logo Image")

    class Meta:
        verbose_name = "Logo"
        verbose_name_plural = "Logos"
        ordering = ['-id']

    def __str__(self):
        return f"Logo ID: {self.id} "
  

