# Generated by Django 5.0.7 on 2024-12-19 04:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_remove_logo_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='logo',
            name='logo_type',
            field=models.CharField(choices=[('chatbot', 'Chatbot Logo'), ('main', 'Main Logo')], default='main', max_length=30),
        ),
    ]