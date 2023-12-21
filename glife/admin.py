from django.contrib import admin
from .models import (
    RestorationPromptTemplate,
    RestorationJob,
)
from django.contrib.admin import register, ModelAdmin
from core.admin import PromptTemplateAdmin, TextProcessingJobAdmin
from core.admin_actions import datasource_importjson


@register(RestorationPromptTemplate)
class RestorationPromptTemplateAdmin(PromptTemplateAdmin):
    pass


@register(RestorationJob)
class RestorationJobAdmin(TextProcessingJobAdmin):
    pass
