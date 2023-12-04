# Generated by Django 4.2.7 on 2023-12-04 20:57

from django.db import migrations, models
import django.db.models.deletion
import glife.models
import glife.models_validators


class Migration(migrations.Migration):

    dependencies = [
        ('glife', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlteredText',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('alteration_function', models.CharField(editable=False, max_length=200)),
                ('alteration_function_kwargs', models.TextField(editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='originaltext',
            name='text_md5',
            field=models.CharField(default='default', editable=False, max_length=32, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='datasource',
            name='json_file',
            field=models.FileField(help_text='Upload a JSON file containing the data for this data source.', upload_to=glife.models.datasource_upload_path, validators=[glife.models_validators.datasource_validate_json], verbose_name='JSON File'),
        ),
        migrations.CreateModel(
            name='ProcessedText',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('processing_function', models.CharField(editable=False, max_length=200)),
                ('processing_function_kwargs', models.TextField(editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('altered_text', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='glife.alteredtext')),
            ],
        ),
        migrations.AddField(
            model_name='alteredtext',
            name='original_text',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='glife.originaltext'),
        ),
    ]