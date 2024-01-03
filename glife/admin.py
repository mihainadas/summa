from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from .models import (
    RestorationPromptTemplate,
    RestorationJob,
    RestorationJobRun,
    RestorationJobRunOutput,
    RestorationOutput,
)
from django.contrib.admin import register, ModelAdmin
from core.admin import (
    PromptTemplateAdmin,
    TextProcessingJobAdmin,
    TextProcessingJobRunAdmin,
    TextProcessingOutputAdmin,
)


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
