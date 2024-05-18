# Generated by Django 4.2.7 on 2024-05-18 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_llm_version_alter_textprocessingjobrun_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='llm',
            name='model',
            field=models.CharField(editable=False, max_length=200, verbose_name='Model Vendor'),
        ),
        migrations.AlterField(
            model_name='llm',
            name='version',
            field=models.CharField(choices=[('SUMMA_ECHO', 'SUMMA_ECHO'), ('OPENAI_GPT_3_5_TURBO', 'OPENAI_GPT_3_5_TURBO'), ('OPENAI_GPT_4', 'OPENAI_GPT_4'), ('OPENAI_GPT_4_TURBO', 'OPENAI_GPT_4_TURBO'), ('OPENAI_GPT_4o', 'OPENAI_GPT_4o'), ('GOOGLE_GEMINI_1_0_PRO', 'GOOGLE_GEMINI_1_0_PRO'), ('GOOGLE_GEMINI_1_5_PRO', 'GOOGLE_GEMINI_1_5_PRO'), ('GOOGLE_GEMINI_1_5_FLASH', 'GOOGLE_GEMINI_1_5_FLASH'), ('META_LLAMA_2_7B_CHAT_HF', 'META_LLAMA_2_7B_CHAT_HF'), ('META_LLAMA_2_70B_CHAT_HF', 'META_LLAMA_2_70B_CHAT_HF'), ('META_LLAMA_3_8B_INSTRUCT', 'META_LLAMA_3_8B_INSTRUCT'), ('META_LLAMA_3_70B_INSTRUCT', 'META_LLAMA_3_70B_INSTRUCT'), ('DEEPINFRA_AIROBOROS_70B', 'DEEPINFRA_AIROBOROS_70B'), ('MISTRALAI_MIXTRAL_8X7B_INSTRUCT_V0_1', 'MISTRALAI_MIXTRAL_8X7B_INSTRUCT_V0_1'), ('OPENLLMRO_ROLLAMA_2_7B_CHAT_V1', 'OPENLLMRO_ROLLAMA_2_7B_CHAT_V1')], max_length=200, unique=True, verbose_name='Model Version'),
        ),
        migrations.AlterField(
            model_name='textprocessor',
            name='name',
            field=models.CharField(choices=[('BASIC', 'Basic Text Processor'), ('EXPONENTIAL_BACKOFF', 'Exponential Backoff Text Processor')], max_length=200, unique=True),
        ),
    ]
