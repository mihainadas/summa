from django.contrib import admin
from .models import DataSource, OriginalText, PreprocessedText
from .admin_actions import datasource_importjson, originaltext_preprocess
from django.contrib.admin import register, ModelAdmin


@register(DataSource)
class DataSourceAdmin(ModelAdmin):
    list_display = ("name", "description", "json_file")
    list_filter = ("name",)
    actions = [datasource_importjson]


@register(OriginalText)
class OriginalTextAdmin(ModelAdmin):
    list_display = ("data_source", "text")
    list_filter = ("data_source",)
    readonly_fields = ("text_md5",)
    actions = [originaltext_preprocess]


@register(PreprocessedText)
class PreprocessedTextAdmin(ModelAdmin):
    list_display = (
        "original_text",
        "text",
        "preprocessing_function",
        "preprocessing_function_kwargs",
        "created_at",
    )
    list_filter = ("original_text",)
    readonly_fields = (
        "preprocessing_function",
        "preprocessing_function_kwargs",
        "created_at",
    )
