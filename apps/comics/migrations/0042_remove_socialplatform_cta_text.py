# Generated by Django 3.0.7 on 2020-06-21 15:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comics', '0041_auto_20200621_1553'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='socialplatform',
            name='cta_text',
        ),
    ]