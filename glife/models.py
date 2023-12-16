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


def short_text(text):
    words = text.split()[:10]
    truncated_text = " ".join(words)
    if len(words) < len(text.split()):
        truncated_text += "..."
    return truncated_text


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
        return f"{short_text(self.text)} ({self.data_source})"


class PreprocessedText(models.Model):
    original_text = models.ForeignKey(OriginalText, on_delete=models.CASCADE)
    text = models.TextField()
    preprocessing_function = models.CharField(max_length=200, editable=False)
    preprocessing_function_kwargs = models.TextField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{short_text(self.text)} ({self.original_text})"

    def save(self, *args, **kwargs):
        # Check if a record with the same preprocessing_function and preprocessing_function_kwargs already exists
        if PreprocessedText.objects.filter(
            preprocessing_function=self.preprocessing_function,
            preprocessing_function_kwargs=self.preprocessing_function_kwargs,
        ).exists():
            raise django.core.exceptions.ValidationError(
                "A record with the same preprocessing_function and preprocessing_function_kwargs already exists."
            )
        super().save(*args, **kwargs)


class ProcessedText(models.Model):
    altered_text = models.ForeignKey(PreprocessedText, on_delete=models.CASCADE)
    text = models.TextField()
    processing_function = models.CharField(max_length=200, editable=False)
    processing_function_kwargs = models.TextField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{short_text(self.text)} ({self.altered_text})"
