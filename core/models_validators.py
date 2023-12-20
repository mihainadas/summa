import json
import jsonschema
import django.core.exceptions
import logging

logger = logging.getLogger(__name__)

# Define the JSON schema for the datasource
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


# Function to validate the JSON data against the schema
def datasource_validate_json(value):
    try:
        # Load the JSON data from the file
        json_data = json.load(value.file)

        # Validate the JSON data against the schema
        jsonschema.validate(json_data, datasource_json_schema)
    except (jsonschema.ValidationError, json.JSONDecodeError) as e:
        # Log the exception and raise a validation error
        logger.exception(f"JSON validation against schema failed: {str(e)}")
        raise django.core.exceptions.ValidationError(f"Invalid JSON: {str(e)}")
