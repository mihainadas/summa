from django.db import models
from core.models import PromptTemplate, TextProcessingJob


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
