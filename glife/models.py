import os
import json
import jsonschema
import django.core.exceptions
from django.db import models
from django.utils.text import slugify
from datetime import datetime

json_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "text": {"type": "string"},
        },
        "required": ["text"],
        "additionalProperties": True,
    },
}


def validate_json(value):
    try:
        json_data = json.load(value.file)
        jsonschema.validate(json_data, json_schema)
    except (jsonschema.ValidationError, json.JSONDecodeError) as e:
        raise django.core.exceptions.ValidationError(f"Invalid JSON: {str(e)}")


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
        validators=[validate_json],
    )

    def __str__(self):
        return self.name


class OriginalText(models.Model):
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return f"{self.text} ({self.data_source})"
