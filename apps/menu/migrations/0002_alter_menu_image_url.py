# Generated migration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menu',
            name='image_url',
            field=models.URLField(blank=True, help_text='ImgBB image URL', max_length=500, null=True),
        ),
    ]
