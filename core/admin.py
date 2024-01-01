from .admin_actions import (
    datasource_importjson,
    datasource_slugify_name,
    textprocessingjob_run,
)
from django.contrib import admin
from django.contrib.admin import register, ModelAdmin
from django.utils.safestring import mark_safe
from .models import (
    JSONDataSource,
    LLM,
    Evaluator,
    TextPreprocessor,
    TextProcessor,
    TextProcessingJob,
    TextProcessingJobRun,
    TextProcessingJobRunOutput,
    TextProcessingEvaluatorOutput,
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


@register(Evaluator)
class EvaluatorAdmin(ModelAdmin):
    list_display = ("name", "description")
    list_filter = ("name",)


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


class TextProcessingJobRunInline(admin.TabularInline):
    model = TextProcessingJobRun


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
    actions = [textprocessingjob_run]

    inlines = [
        TextProcessingJobRunInline,
    ]

    def llms_count(self, obj):
        return obj.llms.count()

    llms_count.short_description = "LLMs"

    def prompt_templates_count(self, obj):
        return obj.prompt_templates.count()

    prompt_templates_count.short_description = "Prompt Templates"

    def has_change_permission(self, request, obj=None):
        return False


class TextProcessingJobRunOutputInline(admin.TabularInline):
    model = TextProcessingJobRunOutput


class TextProcessingJobRunAdmin(ModelAdmin):
    list_display = (
        "id",
        "job",
        "created_at",
        "runtime",
        "outputs_count",
        "runtime_per_output",
    )
    list_filter = (
        "job",
        "job__preprocessor",
        "job__processor",
        "job__llms",
    )
    readonly_fields = ("created_at",)
    inlines = [
        TextProcessingJobRunOutputInline,
    ]

    def has_change_permission(self, request, obj=None):
        return False

    def runtime(self, obj):
        if obj.finished_at and obj.started_at:
            runtime = obj.finished_at - obj.started_at
            minutes = runtime.seconds // 60
            seconds = runtime.seconds % 60
            return f"{minutes} minutes {seconds} seconds"
        else:
            return None

    def outputs_count(self, obj):
        return obj.textprocessingjobrunoutput_set.count()

    outputs_count.short_description = "Outputs"

    def runtime_per_output(self, obj):
        outputs = self.outputs_count(obj)
        if obj.finished_at and obj.started_at:
            runtime = (obj.finished_at - obj.started_at) / outputs
            minutes = runtime.seconds // 60
            seconds = runtime.seconds % 60
            return f"{minutes} minutes {seconds} seconds"
        else:
            return None

    runtime_per_output.short_description = "Runtime per Output"


class TextProcessingEvaluatorOutputInline(admin.TabularInline):
    model = TextProcessingEvaluatorOutput


class TextProcessingOutputAdmin(ModelAdmin):
    list_display = (
        "id",
        "llm",
        "prompt_template",
        "output",
        "generation_time",
    )
    list_filter = (
        "llm",
        "prompt_template",
    )

    inlines = [
        TextProcessingEvaluatorOutputInline,
    ]

    def has_change_permission(self, request, obj=None):
        return False
