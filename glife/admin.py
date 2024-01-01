from django.contrib import admin
from .models import (
    RestorationPromptTemplate,
    RestorationJob,
    RestorationJobRun,
    RestorationOutput,
)
from django.contrib.admin import register, ModelAdmin
from core.admin import (
    PromptTemplateAdmin,
    TextProcessingJobAdmin,
    TextProcessingJobRunAdmin,
    TextProcessingOutputAdmin,
)
from core.admin_actions import datasource_importjson


@register(RestorationPromptTemplate)
class RestorationPromptTemplateAdmin(PromptTemplateAdmin):
    pass


@register(RestorationJob)
class RestorationJobAdmin(TextProcessingJobAdmin):
    pass


@register(RestorationJobRun)
class RestorationJobRunAdmin(TextProcessingJobRunAdmin):
    pass


@register(RestorationOutput)
class RestorationOutputAdmin(TextProcessingOutputAdmin):
    pass
