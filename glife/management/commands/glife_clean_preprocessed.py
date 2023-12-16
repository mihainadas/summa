import logging
import time
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from glife.models import OriginalText, PreprocessedText

# Set up logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Deletes all preprocessed texts"

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            # Get all preprocessed texts
            preprocessed_texts = PreprocessedText.objects.all()
            logger.info(f"Found {len(preprocessed_texts)} preprocessed texts to delete")

            start_time = time.time()

            # Delete all preprocessed texts in a single SQL command
            num_deleted, _ = preprocessed_texts.delete()

            end_time = time.time()
            elapsed_time = end_time - start_time

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully deleted {num_deleted} preprocessed texts in {elapsed_time:.2f} seconds."
                )
            )
            logger.info(
                f"Successfully deleted {num_deleted} preprocessed texts in {elapsed_time:.2f} seconds."
            )

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise CommandError(f"An error occurred: {e}")
