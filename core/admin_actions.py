import json
import logging
from .models import RawText
from django.contrib import messages, admin
from django.utils.text import slugify


logger = logging.getLogger(__name__)


@admin.action(description="Import JSON data for selected %(verbose_name_plural)s")
def datasource_importjson(modeladmin, request, queryset):
    saved_texts_count = 0
    failed_texts_count = 0
    for datasource in queryset:
        json_data = json.load(datasource.file)
        for item in json_data:
            text = RawText(
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


@admin.action(description="Slugify name for selected %(verbose_name_plural)s")
def datasource_slugify_name(modeladmin, request, queryset):
    for datasource in queryset:
        datasource.name = slugify(datasource.name).upper()
        datasource.save()
