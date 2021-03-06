# Generated by Django 3.0.1 on 2019-12-31 01:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('comics', '0030_auto_20191229_0516'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comic',
            name='hr_image',
        ),
        migrations.AlterField(
            model_name='styleconfiguration',
            name='comic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='style_configurations', to='comics.Comic'),
        ),
        migrations.AlterField(
            model_name='styleconfiguration',
            name='property',
            field=models.CharField(choices=[('overflow-background', 'Overflow Background'), ('content-background', 'Content Background'), ('primary-text-color', 'Primary Text Color'), ('footer-background-color', 'Footer Background Color'), ('tag-background-color', 'Tag Background Color'), ('tag-text-color', 'Tag Text Color'), ('spinner-image', 'Spinner Image'), ('navigation-spritesheet', 'Navigation Spritesheet'), ('post-border-image', 'Post Border Image')], help_text="Use CSS property values. For colors, that's like `#000000FF` and for images that's like `url(https://placekitten.com/120/120/)`", max_length=32),
        ),
    ]
