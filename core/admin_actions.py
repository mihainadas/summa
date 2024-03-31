import json
import logging
from .models import RawText, TextProcessingJobRun
from django.contrib import messages, admin
from django.utils.text import slugify

from background_task import background


logger = logging.getLogger(__name__)


@admin.action(description="Slugify name for selected %(verbose_name_plural)s")
def datasource_slugify_name(modeladmin, request, queryset):
    for datasource in queryset:
        datasource.name = slugify(datasource.name).upper()
        datasource.save()


@background(schedule=0)
def _task_textprocessingjob_run(run_id):
    logger.info(f"TextProcessingJobRun {run_id} scheduled for background execution.")
    TextProcessingJobRun.objects.get(id=run_id).run()


@admin.action(description="Run selected %(verbose_name_plural)s")
def textprocessingjob_run(modeladmin, request, queryset):
    for textprocessingjob in queryset:
        run_id = textprocessingjob.create_run()
        _task_textprocessingjob_run(run_id)
        messages.info(
            request, f"Created Job Run {run_id}. Check Background Tasks for status."
        )


@background(schedule=0)
def _task_textprocessingjobrun_recover(run_id):
    logger.info(f"TextProcessingJobRun {run_id} scheduled for background execution.")
    TextProcessingJobRun.objects.get(id=run_id).run(recover=True)


@admin.action(description="Recover selected %(verbose_name_plural)s")
def textprocessingjobrun_recover(modeladmin, request, queryset):
    for textprocessingjobrun in queryset:
        run_id = textprocessingjobrun.id
        _task_textprocessingjobrun_recover(run_id)
        messages.info(
            request,
            f"Initiated recovery of Job Run {textprocessingjobrun.id}. Check Background Tasks for status.",
        )
