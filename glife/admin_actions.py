import json
import logging
from .models import OriginalText, PreprocessedText, ProcessedText
from django.contrib import messages, admin
from summa.preprocessors import StripDiacritics

logger = logging.getLogger(__name__)


# Takes a queryset of OriginalText objects and creates an AlteredText object for each one.
@admin.action(description="Preprocess selected %(verbose_name_plural)s)")
def originaltext_preprocess(modeladmin, request, queryset):
    preprocessed_texts_count = 0
    failed_texts_count = 0
    sd = StripDiacritics()
    for original_text in queryset:
        text = PreprocessedText(
            original_text=original_text,
            text=sd.preprocess(text=original_text.text),
            preprocessing_function=f"{sd.__class__}.{sd.__name__}",
            preprocessing_function_kwargs={"text": {original_text.text}},
        )
        try:
            text.save()
            preprocessed_texts_count += 1
        except Exception as e:
            logger.exception(f"Failed to preprocess text: {str(e)}")
            modeladmin.message_user(
                request,
                f"Failed to preprocess text: {str(e)}",
                messages.ERROR,
            )
            failed_texts_count += 1

    if failed_texts_count == 0:
        modeladmin.message_user(
            request,
            f"Preprocessed {preprocessed_texts_count} texts.",
            messages.SUCCESS,
        )
    else:
        modeladmin.message_user(
            request,
            f"Preprocessed {preprocessed_texts_count} texts. Failed to preprocess {failed_texts_count} texts.",
            messages.WARNING,
        )


# Takes a queryset of PreprocessedText objects and creates a ProcessedText object for each one.
@admin.action(description="Process selected %(verbose_name_plural)s)")
def preprocessedtext_process(modeladmin, request, queryset):
    processed_texts_count = 0
    failed_texts_count = 0
    for original_text in queryset:
        text = ProcessedText(
            original_text=original_text,
            text=strip_diacritics(text=original_text.text),
            processing_function=f"{strip_diacritics.__module__}.{strip_diacritics.__name__}",
            processing_function_kwargs={"text": original_text.text},
        )
        try:
            text.save()
            processed_texts_count += 1
        except Exception as e:
            logger.exception(f"Failed to process text: {str(e)}")
            modeladmin.message_user(
                request,
                f"Failed to process text: {str(e)}",
                messages.ERROR,
            )
            failed_texts_count += 1

    if failed_texts_count == 0:
        modeladmin.message_user(
            request,
            f"Processed {processed_texts_count} texts.",
            messages.SUCCESS,
        )
    else:
        modeladmin.message_user(
            request,
            f"Processed {processed_texts_count} texts. Failed to process {failed_texts_count} texts.",
            messages.WARNING,
        )
