# Generated by Django 3.2.15 on 2022-08-24 02:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comics', '0054_auto_20220821_0820'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
