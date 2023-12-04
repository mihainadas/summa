import json
import logging
from .models import DataSource, OriginalText
from django.contrib import messages, admin

logger = logging.getLogger(__name__)


@admin.action(description="Import JSON")
def datasource_import_json(modeladmin, request, queryset):
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
