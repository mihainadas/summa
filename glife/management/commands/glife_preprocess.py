import logging
import time
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from glife.models import OriginalText, PreprocessedText
from summa.preprocessors import strip_diacritics

# Set up logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Strips diacritics from original texts that haven't been preprocessed yet"

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            # Get all original texts that haven't been preprocessed yet
            original_texts = OriginalText.objects.filter(preprocessedtext__isnull=True)
            logger.info(f"Found {len(original_texts)} original texts to preprocess")

            start_time = time.time()

            # Strip diacritics from each original text
            for original_text in original_texts:
                preprocessed_text = strip_diacritics(original_text.text)
                preprocessed_text_obj = PreprocessedText(
                    original_text=original_text,
                    text=preprocessed_text,
                    preprocessing_function=f"{strip_diacritics.__module__}.{strip_diacritics.__name__}",
                    preprocessing_function_kwargs={"text": {original_text.text}},
                )
                preprocessed_text_obj.save()

            end_time = time.time()
            elapsed_time = end_time - start_time

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully stripped diacritics from {len(original_texts)} original texts in {elapsed_time:.2f} seconds."
                )
            )
            logger.info(
                f"Successfully stripped diacritics from {len(original_texts)} original texts in {elapsed_time:.2f} seconds."
            )

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise CommandError(f"An error occurred: {e}")
