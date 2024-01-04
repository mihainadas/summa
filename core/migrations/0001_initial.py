# Generated by Django 4.2.7 on 2024-01-04 13:46

import core.models
import core.models_validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Evaluator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('RA_CS_CL', 'RA (Case Sensitive, Character Level, Padding Stripped)'), ('RA_CI_CL', 'RA (Case Insensitive, Character Level, Padding Stripped)'), ('RA_CS_WL', 'RA (Case Sensitive, Word Level, Padding Stripped)'), ('RA_CI_WL', 'RA (Case Insensitive, Word Level, Padding Stripped)'), ('RER_CS_CL', 'RER (Case Sensitive, Character Level, Padding Stripped)'), ('RER_CI_CL', 'RER (Case Insensitive, Character Level, Padding Stripped)'), ('RER_CS_WL', 'RER (Case Sensitive, Word Level, Padding Stripped)'), ('RER_CI_WL', 'RER (Case Insensitive, Word Level, Padding Stripped)')], max_length=200, unique=True)),
                ('description', models.TextField(editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='JSONDataSource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('file', models.FileField(help_text='Upload a JSON file containing the text data for this data source.', upload_to=core.models.data_source_upload_path, validators=[core.models_validators.datasource_validate_json], verbose_name='JSON File')),
            ],
            options={
                'verbose_name': 'JSON Data Source',
                'verbose_name_plural': 'JSON Data Sources',
            },
        ),
        migrations.CreateModel(
            name='LLM',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model', models.CharField(editable=False, max_length=200)),
                ('version', models.CharField(choices=[('SUMMA_ECHO', 'SUMMA_ECHO'), ('OPENAI_GPT_3_5_TURBO', 'OPENAI_GPT_3_5_TURBO'), ('OPENAI_GPT_4', 'OPENAI_GPT_4'), ('OPENAI_GPT_4_TURBO', 'OPENAI_GPT_4_TURBO'), ('META_LLAMA_2_70B_CHAT_HF', 'META_LLAMA_2_70B_CHAT_HF'), ('META_LLAMA_2_7B_CHAT_HF', 'META_LLAMA_2_7B_CHAT_HF'), ('DEEPINFRA_AIROBOROS_70B', 'DEEPINFRA_AIROBOROS_70B'), ('MISTRALAI_MIXTRAL_8X7B_INSTRUCT_V0_1', 'MISTRALAI_MIXTRAL_8X7B_INSTRUCT_V0_1')], max_length=200, unique=True)),
            ],
            options={
                'verbose_name': 'LLM',
                'verbose_name_plural': 'LLMs',
                'ordering': ['model', 'version'],
            },
        ),
        migrations.CreateModel(
            name='PreprocessedText',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('text_md5', models.CharField(editable=False, max_length=32, verbose_name='MD5 hash')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PromptTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('text_md5', models.CharField(editable=False, max_length=32, verbose_name='MD5 hash')),
                ('file', models.FileField(help_text='Upload a prompt template file.', unique=True, upload_to=core.models.prompt_template_upload_path, verbose_name='Prompt Template File')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='RawText',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('text_md5', models.CharField(editable=False, max_length=32, verbose_name='MD5 hash')),
                ('data_source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.jsondatasource')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TextPreprocessor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('BASIC', 'Basic Text Preprocessor'), ('STRIP_DIACRITICS', 'Strip Diacritics Preprocessor')], max_length=200, unique=True)),
                ('description', models.TextField(editable=False)),
            ],
            options={
                'verbose_name': 'Text Preprocessor',
                'verbose_name_plural': 'Text Preprocessors',
            },
        ),
        migrations.CreateModel(
            name='TextProcessingJob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('data_source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.jsondatasource')),
                ('evaluators', models.ManyToManyField(to='core.evaluator')),
                ('llms', models.ManyToManyField(to='core.llm')),
                ('preprocessor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.textpreprocessor')),
            ],
        ),
        migrations.CreateModel(
            name='TextProcessingJobRun',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('started_at', models.DateTimeField(null=True)),
                ('finished_at', models.DateTimeField(null=True)),
                ('status', models.CharField(choices=[('CREATED', 'Created'), ('STARTED', 'Started'), ('FINISHED', 'Finished'), ('FAILED', 'Failed')], default='CREATED', max_length=200)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.textprocessingjob')),
            ],
        ),
        migrations.CreateModel(
            name='TextProcessingJobRunOutput',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('preprocessed_text', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.preprocessedtext')),
                ('raw_text', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.rawtext')),
                ('run', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.textprocessingjobrun')),
            ],
        ),
        migrations.CreateModel(
            name='TextProcessor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('BASIC', 'Basic Text Processor')], max_length=200, unique=True)),
                ('description', models.TextField(editable=False)),
            ],
            options={
                'verbose_name': 'Text Processor',
                'verbose_name_plural': 'Text Processors',
            },
        ),
        migrations.CreateModel(
            name='TextProcessingOutput',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prompt', models.TextField()),
                ('output', models.TextField()),
                ('generation_time', models.FloatField()),
                ('llm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.llm')),
                ('prompt_template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.prompttemplate')),
                ('run_output', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.textprocessingjobrunoutput')),
            ],
        ),
        migrations.AddField(
            model_name='textprocessingjob',
            name='processor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.textprocessor'),
        ),
        migrations.AddField(
            model_name='textprocessingjob',
            name='prompt_templates',
            field=models.ManyToManyField(to='core.prompttemplate'),
        ),
        migrations.CreateModel(
            name='TextProcessingEvaluatorOutput',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField()),
                ('evaluator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.evaluator')),
                ('processing_output', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.textprocessingoutput')),
            ],
        ),
        migrations.AddField(
            model_name='preprocessedtext',
            name='input',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.rawtext'),
        ),
        migrations.AddField(
            model_name='preprocessedtext',
            name='preprocessor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.textpreprocessor'),
        ),
        migrations.AddIndex(
            model_name='rawtext',
            index=models.Index(fields=['text_md5'], name='core_rawtex_text_md_06aea6_idx'),
        ),
        migrations.AddIndex(
            model_name='preprocessedtext',
            index=models.Index(fields=['text_md5'], name='core_prepro_text_md_d3cb45_idx'),
        ),
    ]
