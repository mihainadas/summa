import json
import logging
from .models import OriginalText, PreprocessedText, ProcessedText
from django.contrib import messages, admin
from summa.preprocessors import strip_diacritics
from summa.processors import restore_diacritics

logger = logging.getLogger(__name__)


@admin.action(description="Import JSON")
def datasource_importjson(modeladmin, request, queryset):
    saved_texts_count = 0
    failed_texts_count = 0
    for datasource in queryset:
        json_data = json.load(datasource.json_file)
        for item in json_data:
            text = OriginalText(
                data_source=datasource,
                text=item["text"],
            )
            try:
                text.save()
                saved_texts_count += 1
            except Exception as e:
                logger.exception(f"Failed to import text from JSON: {str(e)}")
                failed_texts_count += 1

    if failed_texts_count == 0:
        modeladmin.message_user(
            request,
            f"Imported {saved_texts_count} texts.",
            messages.SUCCESS,
        )
    else:
        modeladmin.message_user(
            request,
            f"Imported {saved_texts_count} texts. Failed to import {failed_texts_count} texts.",
            messages.WARNING,
        )


# Takes a queryset of OriginalText objects and creates an AlteredText object for each one.
@admin.action(description="Preprocess")
def originaltext_preprocess(modeladmin, request, queryset):
    preprocessed_texts_count = 0
    failed_texts_count = 0
    for original_text in queryset:
        text = PreprocessedText(
            original_text=original_text,
            text=strip_diacritics(text=original_text.text),
            preprocessing_function=f"{strip_diacritics.__module__}.{strip_diacritics.__name__}",
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
@admin.action(description="Process")
def originaltext_process(modeladmin, request, queryset):
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
