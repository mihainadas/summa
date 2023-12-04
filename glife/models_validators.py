import json
import jsonschema
import django.core.exceptions
import logging

logger = logging.getLogger(__name__)

datasource_json_schema = {
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


def datasource_validate_json(value):
    try:
        json_data = json.load(value.file)
        jsonschema.validate(json_data, datasource_json_schema)
    except (jsonschema.ValidationError, json.JSONDecodeError) as e:
        logger.exception(f"JSON validation against schema failed: {str(e)}")
        raise django.core.exceptions.ValidationError(f"Invalid JSON: {str(e)}")
