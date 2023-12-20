from django.contrib import admin
from .models import (
    RestorationPromptTemplate,
    OriginalText,
    StrippedText,
    RestoredText,
)
from django.contrib.admin import register, ModelAdmin
from core.admin import DataSourceAdmin, PromptTemplateAdmin as PromptTemplateAdmin
from core.admin_actions import datasource_importjson


@register(RestorationPromptTemplate)
class RestorationPromptTemplateAdmin(PromptTemplateAdmin):
    pass


@register(OriginalText)
class OriginalTextAdmin(ModelAdmin):
    list_display = (
        "data_source",
        "text",
    )
    list_filter = ("data_source",)
    readonly_fields = ("text_md5",)


@register(StrippedText)
class StrippedTextAdmin(ModelAdmin):
    list_display = (
        "input",
        "text",
        "created_at",
    )
    list_filter = ("input",)
    readonly_fields = ("created_at",)
