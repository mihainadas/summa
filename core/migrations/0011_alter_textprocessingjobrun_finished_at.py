# Generated by Django 4.2.7 on 2023-12-31 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_textprocessingjobrun_started_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='textprocessingjobrun',
            name='finished_at',
            field=models.DateTimeField(null=True),
        ),
    ]
