from django.db import models
from core.models import (
    PromptTemplate,
    TextProcessingJob,
    TextProcessingJobRun,
    TextProcessingOutput,
)


class RestorationPromptTemplate(PromptTemplate):
    class Meta:
        proxy = True
        verbose_name = "Restoration Prompt Template"
        verbose_name_plural = "Restoration Prompt Templates"


class RestorationJob(TextProcessingJob):
    class Meta:
        proxy = True
        verbose_name = "Restoration Job"
        verbose_name_plural = "Restoration Jobs"


class RestorationJobRun(TextProcessingJobRun):
    class Meta:
        proxy = True
        verbose_name = "Restoration Job Run"
        verbose_name_plural = "Restoration Job Runs"


class RestorationJobRunOutput(TextProcessingOutput):
    class Meta:
        proxy = True
        verbose_name = "Restoration Job Run Output"
        verbose_name_plural = "Restoration Job Run Outputs"


class RestorationOutput(TextProcessingOutput):
    class Meta:
        proxy = True
        verbose_name = "Restoration Output"
        verbose_name_plural = "Restoration Outputs"
