# Generated by Django 4.2.7 on 2023-12-16 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('glife', '0002_alteredtext_originaltext_text_md5_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AlteredText',
            new_name='PreprocessedText',
        ),
        migrations.AlterField(
            model_name='originaltext',
            name='text_md5',
            field=models.CharField(editable=False, max_length=32, unique=True, verbose_name='MD5 hash'),
        ),
    ]