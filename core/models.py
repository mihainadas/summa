import json
import os
import logging
import django.core.exceptions
import concurrent.futures
import summa
from django.db import models, transaction
from django.db.utils import IntegrityError
from django.utils.text import slugify
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone
from .utils import short_text, md5
from .models_validators import datasource_validate_json
from summa.llms import ModelVersions, TextGenerationLLMs, TextGenerationLLM
from summa.preprocessors import TextPreprocessors, TextPreprocessor
from summa.processors import TextProcessors, TextProcessor
from summa.evals import Evaluators
from summa.pipelines import PipelineRunner, PipelineRunOutput

logger = logging.getLogger(__name__)


def _upload_path(instance, filename, prefix):
    base, extension = os.path.splitext(filename)
    timestamp = timezone.now().strftime("%y%m%d_%H%M")
    adjusted_filename = f"{slugify(base)}-{timestamp}{extension}"
    module_name = instance.__class__.__module__.split(".")[0]
    return "{0}/{1}/{2}".format(module_name, prefix, adjusted_filename)


class TextModel(models.Model):
    text = models.TextField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.text

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

    class Meta:
        abstract = True


def data_source_upload_path(instance, filename):
    return _upload_path(instance, filename, "data_sources")


class JSONDataSource(models.Model):
    name = models.CharField(max_length=200)

    file = models.FileField(
        upload_to=data_source_upload_path,
        verbose_name="JSON File",
        help_text="Upload a JSON file containing the text data for this data source.",
        validators=[datasource_validate_json],
    )

    @property
    def json(self):
        return json.load(self.file)

    @property
    def texts(self):
        return [d["text"] for d in self.json]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "JSON Data Source"
        verbose_name_plural = "JSON Data Sources"


class RawText(MD5TextModel):
    data_source = models.ForeignKey(JSONDataSource, on_delete=models.CASCADE)


class TextPreprocessor(models.Model):
    name = models.CharField(
        max_length=200,
        choices=[(v.name, v.value.name) for v in TextPreprocessors],
        unique=True,
    )
    description = models.TextField(editable=False)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.description = TextPreprocessors[self.name].value.description
        super().save(*args, **kwargs)

    @property
    def instance(self) -> TextPreprocessor:
        return TextPreprocessors[self.name].value

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Text Preprocessor"
        verbose_name_plural = "Text Preprocessors"


class TextProcessor(models.Model):
    name = models.CharField(
        max_length=200,
        choices=[(v.name, v.value.name) for v in TextProcessors],
        unique=True,
    )
    description = models.TextField(editable=False)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.description = TextProcessors[self.name].value.description
        super().save(*args, **kwargs)

    @property
    def instance(self) -> TextProcessor:
        return TextProcessors[self.name].value

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Text Processor"
        verbose_name_plural = "Text Processors"


def prompt_template_upload_path(instance, filename):
    return _upload_path(instance, filename, "prompt_templates")


class PromptTemplate(MD5TextModel):
    file = models.FileField(
        upload_to=prompt_template_upload_path,
        verbose_name="Prompt Template File",
        help_text="Upload a prompt template file.",
        unique=True,
    )

    def save(self, *args, **kwargs):
        if isinstance(self.file.file, InMemoryUploadedFile):
            self.text = self.file.file.read().decode("utf-8")
        super().save(*args, **kwargs)

    @property
    def instance(self) -> str:
        return summa.llms.PromptTemplate(template_filename=self.file.path)

    def __str__(self):
        return f"{os.path.basename(self.file.name)}"

    class Meta:
        ordering = ["id"]


class LLM(models.Model):
    model = models.CharField(max_length=200, editable=False)
    version = models.CharField(
        max_length=200,
        choices=[(v.name, v.name) for v in TextGenerationLLMs],
        unique=True,
    )

    def save(self, *args, **kwargs):
        if self.model is None or self.model == "":
            self.model = TextGenerationLLMs[self.version].value.model
        super().save(*args, **kwargs)

    # TODO: When implementing new types of LLMs, the property below needs to be updated to return the correct type (e.g. instead of TextGenerationLLM, it should return the new type)
    @property
    def instance(self) -> TextGenerationLLM:
        # TODO: This is where a CASE-like statement should be used to return the correct type of LLM, based on the model type (which should be added to the Django Model)
        return TextGenerationLLMs[self.version].value

    def __str__(self):
        return f"{self.model} - {self.version}"

    class Meta:
        verbose_name = "LLM"
        verbose_name_plural = "LLMs"
        ordering = ["model", "version"]


class Evaluator(models.Model):
    name = models.CharField(
        max_length=200,
        choices=[(v.name, v.value.name) for v in Evaluators],
        unique=True,
    )
    description = models.TextField(editable=False)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.description = Evaluators[self.name].value.description
        super().save(*args, **kwargs)

    @property
    def instance(self) -> Evaluators:
        return Evaluators[self.name].value

    def __str__(self):
        return self.name


class PreprocessedText(TextModel):
    preprocessor = models.ForeignKey(TextPreprocessor, on_delete=models.CASCADE)
    input = models.ForeignKey(RawText, on_delete=models.CASCADE)


class ProcessedText(TextModel):
    processor = models.ForeignKey(TextProcessor, on_delete=models.CASCADE)
    input = models.ForeignKey(PreprocessedText, on_delete=models.CASCADE)
    llm = models.ForeignKey(LLM, on_delete=models.CASCADE)
    prompt_template = models.ForeignKey(PromptTemplate, on_delete=models.CASCADE)
    prompt = models.TextField()
    generation_time = models.FloatField()


class TextProcessingJobRun(models.Model):
    class Statuses(models.TextChoices):
        CREATED = "CREATED", "Created"
        STARTED = "STARTED", "Started"
        FINISHED = "FINISHED", "Finished"
        FAILED = "FAILED", "Failed"

    job = models.ForeignKey("TextProcessingJob", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True)
    finished_at = models.DateTimeField(null=True)
    status = models.CharField(
        max_length=200, choices=Statuses.choices, default=Statuses.CREATED
    )

    def set_start(self):
        self.status = TextProcessingJobRun.Statuses.STARTED
        self.started_at = timezone.now()
        self.save()

    def set_finish(self):
        self.status = TextProcessingJobRun.Statuses.FINISHED
        self.finished_at = timezone.now()
        self.save()

    @transaction.atomic
    def _save_output(self, job: "TextProcessingJob", output: PipelineRunOutput):
        raw_text, _ = RawText.objects.get_or_create(
            data_source=job.data_source, text=output.raw_text
        )
        run_output = TextProcessingJobRunOutput.objects.create(
            run=self,
            raw_text=raw_text,
            preprocessed_text=PreprocessedText.objects.create(
                preprocessor=job.preprocessor,
                input=raw_text,
                text=output.preprocessed_text,
            ),
        )
        for processed_output in output.processed_outputs:
            processing_output = TextProcessingOutput.objects.create(
                run_output=run_output,
                llm=job.llms.get(
                    version=ModelVersions(processed_output.model_version).name
                ),
                prompt_template=job.prompt_templates.get(
                    text=processed_output.prompt_template
                ),
                prompt=processed_output.prompt,
                output=processed_output.output,
                generation_time=processed_output.generation_time,
            )
            for evaluator_output in processed_output.evals:
                TextProcessingEvaluatorOutput.objects.create(
                    processing_output=processing_output,
                    evaluator=job.evaluators.get(
                        name=Evaluators(evaluator_output.evaluator).name
                    ),
                    score=evaluator_output.score,
                )

    def run(self):
        preprocessor = self.job.preprocessor.instance
        processor = self.job.processor.instance
        llms = [llm.instance for llm in self.job.llms.all()]
        prompt_templates = [pt.instance for pt in self.job.prompt_templates.all()]
        evaluators = [eval.instance for eval in self.job.evaluators.all()]
        raw_texts = self.job.data_source.texts

        pipeline_runner = PipelineRunner(
            preprocessor, processor, llms, prompt_templates, evaluators
        )

        self.set_start()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(pipeline_runner.run, raw_text) for raw_text in raw_texts
            ]
            for future in concurrent.futures.as_completed(futures):
                try:
                    self._save_output(self.job, future.result())
                except Exception as e:
                    logger.error(e, exc_info=True)

        self.set_finish()


class TextProcessingJob(models.Model):
    data_source = models.ForeignKey(JSONDataSource, on_delete=models.CASCADE)
    preprocessor = models.ForeignKey(TextPreprocessor, on_delete=models.CASCADE)
    processor = models.ForeignKey(TextProcessor, on_delete=models.CASCADE)
    llms = models.ManyToManyField(LLM)
    prompt_templates = models.ManyToManyField(PromptTemplate)
    evaluators = models.ManyToManyField(Evaluator)
    created_at = models.DateTimeField(auto_now_add=True)

    @transaction.atomic
    def _save_output(self, run: TextProcessingJobRun, output: PipelineRunOutput):
        raw_text, _ = RawText.objects.get_or_create(
            data_source=self.data_source, text=output.raw_text
        )
        run_output = TextProcessingJobRunOutput.objects.create(
            run=run,
            raw_text=raw_text,
            preprocessed_text=PreprocessedText.objects.create(
                preprocessor=self.preprocessor,
                input=raw_text,
                text=output.preprocessed_text,
            ),
        )
        for processed_output in output.processed_outputs:
            processing_output = TextProcessingOutput.objects.create(
                run_output=run_output,
                llm=self.llms.get(
                    version=ModelVersions(processed_output.model_version).name
                ),
                prompt_template=self.prompt_templates.get(
                    text=processed_output.prompt_template
                ),
                prompt=processed_output.prompt,
                output=processed_output.output,
                generation_time=processed_output.generation_time,
            )
            for evaluator_output in processed_output.evals:
                TextProcessingEvaluatorOutput.objects.create(
                    processing_output=processing_output,
                    evaluator=self.evaluators.get(
                        name=Evaluators(evaluator_output.evaluator).name
                    ),
                    score=evaluator_output.score,
                )

    def run(self):
        job_run = TextProcessingJobRun.objects.create(job=self)

        preprocessor = self.preprocessor.instance
        processor = self.processor.instance
        llms = [llm.instance for llm in self.llms.all()]
        prompt_templates = [pt.instance for pt in self.prompt_templates.all()]
        evaluators = [eval.instance for eval in self.evaluators.all()]
        raw_texts = self.data_source.texts

        pipeline_runner = PipelineRunner(
            preprocessor, processor, llms, prompt_templates, evaluators
        )

        job_run.set_start()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(pipeline_runner.run, raw_text) for raw_text in raw_texts
            ]
            for future in concurrent.futures.as_completed(futures):
                try:
                    self._save_output(job_run, future.result())
                except Exception as e:
                    logger.error(e, exc_info=True)

        job_run.set_finish()

    def create_run(self):
        job_run = TextProcessingJobRun.objects.create(job=self)
        return job_run.id

    def __str__(self):
        return f"Job #{self.id} - '{self.data_source.name}' ({self.created_at:%Y-%m-%d %H:%M:%S})"


class TextProcessingJobRunOutput(models.Model):
    run = models.ForeignKey(TextProcessingJobRun, on_delete=models.CASCADE)
    raw_text = models.ForeignKey(RawText, on_delete=models.CASCADE)
    preprocessed_text = models.ForeignKey(PreprocessedText, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class TextProcessingOutput(models.Model):
    run_output = models.ForeignKey(TextProcessingJobRunOutput, on_delete=models.CASCADE)
    llm = models.ForeignKey(LLM, on_delete=models.CASCADE)
    prompt_template = models.ForeignKey(PromptTemplate, on_delete=models.CASCADE)
    prompt = models.TextField()
    output = models.TextField()
    generation_time = models.FloatField()


class TextProcessingEvaluatorOutput(models.Model):
    processing_output = models.ForeignKey(
        TextProcessingOutput, on_delete=models.CASCADE
    )
    evaluator = models.ForeignKey(Evaluator, on_delete=models.CASCADE)
    score = models.FloatField()
