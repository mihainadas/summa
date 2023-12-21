from .admin_actions import datasource_importjson, datasource_slugify_name
from django.contrib.admin import register, ModelAdmin
from django.utils.safestring import mark_safe
from .models import (
    JSONDataSource,
    LLM,
    TextPreprocessor,
    TextProcessor,
    TextProcessingJob,
)


@register(JSONDataSource)
class DataSourceAdmin(ModelAdmin):
    list_display = (
        "name",
        "file",
    )
    list_filter = ("name",)
    actions = [datasource_importjson, datasource_slugify_name]


@register(LLM)
class LLMAdmin(ModelAdmin):
    list_display = (
        "model",
        "version",
    )
    list_filter = (
        "model",
        "version",
    )
    readonly_fields = ("model",)


@register(TextPreprocessor)
class TextPreprocessorAdmin(ModelAdmin):
    list_display = ("name", "description")


@register(TextProcessor)
class TextProcessorAdmin(ModelAdmin):
    list_display = ("name", "description")


class PromptTemplateAdmin(ModelAdmin):
    list_display = ("id", "processed_text", "file")
    list_filter = ("file",)

    def processed_text(self, obj):
        return mark_safe(obj.text.replace("\n", "<br>"))

    processed_text.short_description = "Text"

    def has_change_permission(self, request, obj=None):
        return False


class TextProcessingJobAdmin(ModelAdmin):
    list_display = (
        "id",
        "data_source",
        "preprocessor",
        "processor",
        "llms_count",
        "prompt_templates_count",
        "created_at",
    )
    list_filter = (
        "preprocessor",
        "processor",
        "llms",
    )
    readonly_fields = ("created_at",)

    def llms_count(self, obj):
        return obj.llms.count()

    llms_count.short_description = "LLMs"

    def prompt_templates_count(self, obj):
        return obj.prompt_templates.count()

    prompt_templates_count.short_description = "Prompt Templates"

    def has_change_permission(self, request, obj=None):
        return False
