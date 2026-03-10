# Generated migration for RTU fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('papers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='paper',
            name='branch',
            field=models.CharField(blank=True, help_text='RTU Branch (e.g., CSE, ECE)', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='paper',
            name='semester',
            field=models.CharField(blank=True, help_text='RTU Semester (e.g., 1, 2, 3)', max_length=20, null=True),
        ),
    ]
