from django.db import models
from core.models import (
    PromptTemplate,
    RawText,
    PreprocessedText,
    ProcessedText,
)


class RestorationPromptTemplate(PromptTemplate):
    class Meta:
        proxy = True


class OriginalText(RawText):
    class Meta:
        proxy = True


class StrippedText(PreprocessedText):
    class Meta:
        proxy = True


class RestoredText(ProcessedText):
    class Meta:
        proxy = True
