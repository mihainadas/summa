import os
import django.core.exceptions
import hashlib

from django.db import models
from django.db.utils import IntegrityError
from django.utils.text import slugify
from .models_validators import datasource_validate_json
from datetime import datetime


def datasource_upload_path(instance, filename):
    base, extension = os.path.splitext(filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    adjusted_filename = f"{base}-{timestamp}{extension}"
    return "glife/datasources/{0}/{1}".format(slugify(instance.name), adjusted_filename)


class DataSource(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    json_file = models.FileField(
        upload_to=datasource_upload_path,
        verbose_name="JSON File",
        help_text="Upload a JSON file containing the data for this data source.",
        validators=[datasource_validate_json],
    )

    def __str__(self):
        return self.name


class OriginalText(models.Model):
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    text = models.TextField()
    text_md5 = models.CharField(
        max_length=32, unique=True, editable=False, verbose_name="MD5 hash"
    )

    def save(self, *args, **kwargs):
        self.text_md5 = hashlib.md5(self.text.strip().encode("utf-8")).hexdigest()
        try:
            super().save(*args, **kwargs)
        except IntegrityError:
            raise django.core.exceptions.ValidationError(
                f'Duplicate text found in data source: "{self.text}"'
            )

    def __str__(self):
        return f"{self.text} ({self.data_source})"


class AlteredText(models.Model):
    original_text = models.ForeignKey(OriginalText, on_delete=models.CASCADE)
    text = models.TextField()
    alteration_function = models.CharField(max_length=200, editable=False)
    alteration_function_kwargs = models.TextField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True)


class ProcessedText(models.Model):
    altered_text = models.ForeignKey(AlteredText, on_delete=models.CASCADE)
    text = models.TextField()
    processing_function = models.CharField(max_length=200, editable=False)
    processing_function_kwargs = models.TextField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
