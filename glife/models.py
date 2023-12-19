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


def md5(text):
    return hashlib.md5(text.strip().encode("utf-8")).hexdigest()


class DataSource(models.Model):
    name = models.CharField(max_length=200)
    file = models.FileField(
        upload_to=datasource_upload_path,
        verbose_name="JSON File",
        help_text="Upload a JSON file containing the data for this data source.",
        validators=[datasource_validate_json],
    )

    def __str__(self):
        return self.name


class MD5Text(models.Model):
    text = models.TextField(editable=False)
    text_md5 = models.CharField(
        max_length=32, unique=True, editable=False, verbose_name="MD5 hash"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.text_md5 = md5(self.text)
        try:
            super().save(*args, **kwargs)
        except IntegrityError:
            raise django.core.exceptions.ValidationError(
                f'Duplicate text found in data source: "{self.text}"'
            )

    def __str__(self):
        return f"{short_text(self.text)}"

    class Meta:
        abstract = True


class OriginalText(MD5Text):
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE)


class PreprocessedText(MD5Text):
    original_text = models.ForeignKey(OriginalText, on_delete=models.CASCADE)
    preprocessor = models.CharField(max_length=200, editable=False)
    preprocessor_input = models.TextField(editable=False)


class ProcessedText(MD5Text):
    preprocessed_text = models.ForeignKey(PreprocessedText, on_delete=models.CASCADE)
    processor = models.CharField(max_length=200, editable=False)
    processing_function_kwargs = models.TextField(editable=False)
    model = models.CharField(max_length=200)
    model_version = models.CharField(max_length=200)
    prompt_template = models.CharField(max_length=200)
    prompt_template_path = models.CharField(max_length=200)
    prompt = models.TextField()
    generation_time = models.FloatField()


class Model(models.Model):
    name = models.CharField(max_length=200)
    version = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class PromptTemplate(models.Model):
    file = models.FileField(
        upload_to="glife/prompt_templates",
        verbose_name="Prompt Template File",
        help_text="Upload a prompt template file.",
    )
    template = models.TextField(editable=False)
    template_md5 = models.CharField(
        max_length=32,
        unique=True,
        editable=False,
        verbose_name="MD5 hash",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        with open(self.file.path, "r") as f:
            self.template = f.read()
        self.template_md5 = hashlib.md5(self.text.strip().encode("utf-8")).hexdigest()
        try:
            super().save(*args, **kwargs)
        except IntegrityError:
            raise django.core.exceptions.ValidationError(
                f'Duplicate template found in data source: "{self.text}"'
            )

    def __str__(self):
        return self.name


class Processor(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class ProcessingJob(models.Model):
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    processor = models.ForeignKey(Processor, on_delete=models.CASCADE)
    model = models.ManyToManyField(Model)
    prompt_template = models.ManyToManyField(PromptTemplate)
