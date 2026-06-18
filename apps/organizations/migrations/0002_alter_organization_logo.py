# Generated migration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='logo',
            field=models.URLField(blank=True, help_text='ImgBB logo URL', max_length=500, null=True),
        ),
    ]
