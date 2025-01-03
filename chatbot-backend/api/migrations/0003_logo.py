# Generated by Django 5.1.4 on 2024-12-18 04:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_rename_value_cmscontent_content_chatmessage_language_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Logo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logo', models.ImageField(upload_to='logos/', verbose_name='Logo Image')),
                ('status', models.BooleanField(default=False, verbose_name='Is Active')),
            ],
            options={
                'verbose_name': 'Logo',
                'verbose_name_plural': 'Logos',
                'ordering': ['-id'],
            },
        ),
    ]
