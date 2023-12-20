from .admin_actions import datasource_importjson, datasource_slugify_name
from django.contrib.admin import register, ModelAdmin
from django.utils.safestring import mark_safe
from .models import TextDataSource, LLM


@register(TextDataSource)
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


class PromptTemplateAdmin(ModelAdmin):
    list_display = ("id", "processed_text", "file")
    list_filter = ("file",)

    def processed_text(self, obj):
        return mark_safe(obj.text.replace("\n", "<br>"))

    processed_text.short_description = "Text"

    def has_change_permission(self, request, obj=None):
        return False
