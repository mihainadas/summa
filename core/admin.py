from django.contrib.admin.sites import AdminSite
from .admin_actions import (
    datasource_slugify_name,
    textprocessingjob_run,
    textprocessingjobrun_recover,
)
from django.db.models import Avg
from django.contrib import admin
from django.contrib.admin import register, ModelAdmin
from django.utils.safestring import mark_safe
from django.utils.html import format_html
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
from core.utils import create_admin_link


@register(JSONDataSource)
class DataSourceAdmin(ModelAdmin):
    list_display = (
        "name",
        "file",
    )
    list_filter = ("name",)
    actions = [datasource_slugify_name]


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
        "runs_count",
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

    def has_change_permission(self, request, obj=None):
        return False

    def llms_count(self, obj):
        return obj.llms.count()

    llms_count.short_description = "LLMs"

    def prompt_templates_count(self, obj):
        return obj.prompt_templates.count()

    prompt_templates_count.short_description = "Prompt Templates"

    def runs_count(self, obj):
        return obj.textprocessingjobrun_set.count()


class TextProcessingJobRunOutputInline(admin.TabularInline):
    model = TextProcessingJobRunOutput

    fields = (
        "id",
        "raw_text",
        "preprocessed_text",
        "output_count",
    )

    readonly_fields = ("output_count",)

    def output_count(self, obj):
        count = obj.textprocessingoutput_set.count()
        return create_admin_link(
            obj, "glife", "restorationoutput", "run_output_id", "id", count
        )

    output_count.short_description = "Processed Outputs"


class TextProcessingJobRunAdmin(ModelAdmin):
    list_display = (
        "id",
        "job",
        "created_at",
        "runtime",
        "run_outputs_count",
        "runtime_per_run_output",
        "processed_outputs_count",
        "status",
    )
    list_filter = (
        "job",
        "job__preprocessor",
        "job__processor",
        "job__llms",
    )
    readonly_fields = ("created_at",)
    actions = [textprocessingjobrun_recover]
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
            return f"{minutes} mins {seconds} secs"
        else:
            return None

    def run_outputs_count(self, obj):
        return obj.textprocessingjobrunoutput_set.count()

    run_outputs_count.short_description = "Run Outputs"

    def runtime_per_run_output(self, obj):
        outputs = self.run_outputs_count(obj)
        if obj.finished_at and obj.started_at and outputs > 0:
            runtime = (obj.finished_at - obj.started_at) / outputs
            minutes = runtime.seconds // 60
            seconds = runtime.seconds % 60
            milliseconds = runtime.microseconds // 1000
            return f"{minutes} mins {seconds} secs {milliseconds} ms"
        else:
            return None

    runtime_per_run_output.short_description = "Runtime per Run Output"

    def processed_outputs_count(self, obj):
        return sum(
            [
                o.textprocessingoutput_set.count()
                for o in obj.textprocessingjobrunoutput_set.all()
            ]
        )

    processed_outputs_count.short_description = "Processed Outputs"


class TextProcessingEvaluatorOutputInline(admin.TabularInline):
    model = TextProcessingEvaluatorOutput


class TextProcessingOutputAdmin(ModelAdmin):
    list_display = (
        "id",
        "run_output_id",
        "llm",
        "raw_text",
        "preprocessed_text",
        "output",
        "avg_eval_score",
        "eval_scores",
        "prompt_template",
    )
    list_filter = (
        "run_output__run__job",
        "llm",
        "prompt_template",
        "run_output__run",
        "run_output__run__job__data_source",
    )

    inlines = [
        TextProcessingEvaluatorOutputInline,
    ]

    # Since this is an annotated field, we can't use "ordering" here, hence the hack in get_queryset().
    # ordering = ("avg_eval_score",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            avg_eval_score=Avg("textprocessingevaluatoroutput__score")
        )
        # This is a hack to make the default ordering work with the annotated field. It is necessary because "ordering" doesn't work with annotated fields.
        if request.GET.get("o") is None:
            queryset = queryset.order_by("-avg_eval_score", "-id")
        return queryset

    def has_change_permission(self, request, obj=None):
        return False

    def run_output_id(self, obj):
        return obj.run_output.id

    def raw_text(self, obj):
        return obj.run_output.raw_text

    def preprocessed_text(self, obj):
        return obj.run_output.preprocessed_text

    def avg_eval_score(self, obj):
        return obj.avg_eval_score

    avg_eval_score.short_description = "Avg. Eval. Score"
    avg_eval_score.admin_order_field = "avg_eval_score"

    def eval_scores(self, obj):
        count = obj.textprocessingevaluatoroutput_set.count()
        scores_list = [
            f"<li>{o.evaluator}: {o.score:.4f}</li>"
            for o in obj.textprocessingevaluatoroutput_set.all()
            if o.score is not None
        ]
        return format_html(f"<ul>{''.join(scores_list)}</ul>") if count > 0 else None
