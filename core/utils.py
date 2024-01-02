import hashlib
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.html import format_html


def short_text(text):
    """
    Truncates the given text to a maximum of 10 words and adds ellipsis if necessary.

    Args:
        text (str): The input text to be truncated.

    Returns:
        str: The truncated text.

    """
    words = text.split()[:10]
    truncated_text = " ".join(words)
    if len(words) < len(text.split()):
        truncated_text += "..."
    return truncated_text


def md5(text):
    """
    Calculate the MD5 hash of a given text.

    Args:
        text (str): The text to calculate the MD5 hash for.

    Returns:
        str: The MD5 hash of the input text.
    """
    return hashlib.md5(text.strip().encode("utf-8")).hexdigest()


def create_admin_link(
    obj,
    app_label,
    model_name,
    filter_field_name,
    obj_field_name,
    display_text,
):
    url = reverse(f"admin:{app_label}_{model_name}_changelist")

    url += f"?{filter_field_name}={getattr(obj, obj_field_name)}"

    return format_html('<a href="{}">{}</a>', url, display_text)
