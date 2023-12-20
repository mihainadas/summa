import os
import logging
import django.core.exceptions
from django.db import models
from django.db.utils import IntegrityError
from django.utils.text import slugify
from django.core.files.uploadedfile import InMemoryUploadedFile
from datetime import datetime
from .utils import short_text, md5
from .models_validators import datasource_validate_json
from summa.llms import ModelVersions, ModelFactory

logger = logging.getLogger(__name__)


def _upload_path(instance, filename, prefix):
    base, extension = os.path.splitext(filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    adjusted_filename = f"{slugify(base)}-{timestamp}{extension}"
    module_name = instance.__class__.__module__.split(".")[0]
    return "{0}/{1}/{2}".format(module_name, prefix, adjusted_filename)


class TextModel(models.Model):
    text = models.TextField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{short_text(self.text)}"

    class Meta:
        abstract = True


class MD5TextModel(TextModel):
    text_md5 = models.CharField(
        max_length=32, unique=True, editable=False, verbose_name="MD5 hash"
    )

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


def data_source_upload_path(instance, filename):
    return _upload_path(instance, filename, "data_sources")


class TextDataSource(models.Model):
    name = models.CharField(max_length=200)

    file = models.FileField(
        upload_to=data_source_upload_path,
        verbose_name="JSON File",
        help_text="Upload a JSON file containing the text data for this data source.",
        validators=[datasource_validate_json],
    )

    def __str__(self):
        return self.name


class RawText(MD5TextModel):
    data_source = models.ForeignKey(TextDataSource, on_delete=models.CASCADE)


class TextPreprocessor(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class TextProcessor(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class PreprocessedText(TextModel):
    preprocessor = models.ForeignKey(TextPreprocessor, on_delete=models.CASCADE)
    input = models.ForeignKey(RawText, on_delete=models.CASCADE)


def prompt_template_upload_path(instance, filename):
    return _upload_path(instance, filename, "prompt_templates")


class PromptTemplate(MD5TextModel):
    file = models.FileField(
        upload_to=prompt_template_upload_path,
        verbose_name="Prompt Template File",
        help_text="Upload a prompt template file.",
    )

    def save(self, *args, **kwargs):
        if isinstance(self.file.file, InMemoryUploadedFile):
            self.text = self.file.file.read().decode("utf-8")
        super().save(*args, **kwargs)


class LLM(models.Model):
    model = models.CharField(max_length=200, editable=False)
    version = models.CharField(
        max_length=200, choices=[(v.name, v.name) for v in ModelVersions]
    )

    def save(self, *args, **kwargs):
        if self.model is None or self.model == "":
            self.model = ModelFactory().create(ModelVersions[self.version]).model
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.model} - {self.version}"

    class Meta:
        verbose_name = "LLM"
        verbose_name_plural = "LLMs"


class ProcessedText(TextModel):
    processor = models.ForeignKey(TextProcessor, on_delete=models.CASCADE)
    input = models.ForeignKey(PreprocessedText, on_delete=models.CASCADE)
    llm = models.ForeignKey(LLM, on_delete=models.CASCADE)
    prompt_template = models.ForeignKey(PromptTemplate, on_delete=models.CASCADE)
    prompt = models.TextField()
    generation_time = models.FloatField()


class TextProcessingJob(models.Model):
    data_source = models.ForeignKey(TextDataSource, on_delete=models.CASCADE)
    preprocessor = models.ForeignKey(TextPreprocessor, on_delete=models.CASCADE)
    processor = models.ForeignKey(TextProcessor, on_delete=models.CASCADE)
    llms = models.ManyToManyField(LLM)
    prompt_templates = models.ManyToManyField(PromptTemplate)
    created_at = models.DateTimeField(auto_now_add=True)
