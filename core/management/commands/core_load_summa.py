import logging
from django.core.management.base import BaseCommand
from decouple import config
from summa.preprocessors import TextPreprocessors
from summa.processors import TextProcessors
from summa.llms import TextGenerationLLMs
from summa.evals import Evaluators
from core.models import (
    TextPreprocessor,
    TextProcessor,
    LLM,
    Evaluator,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Load TextPreprocessors, TextProcessors, TextGenerationLLMs and Evaluators from the summa library."

    def _load_preprocessors(self):
        for tp in TextPreprocessors:
            _, created = TextPreprocessor.objects.get_or_create(
                name=tp.name,
                defaults={"description": tp.value.description},
            )
            if created:
                logger.info(f"Loaded TextPreprocessor '{tp.name}'.")
            else:
                logger.info(f"TextPreprocessor '{tp.name}' already exists.")

    def _load_processors(self):
        for tp in TextProcessors:
            _, created = TextProcessor.objects.get_or_create(
                name=tp.name,
                defaults={"description": tp.value.description},
            )
            if created:
                logger.info(f"Loaded TextProcessor '{tp.name}'.")
            else:
                logger.info(f"TextProcessor '{tp.name}' already exists.")

    def _load_llms(self):
        for tp in TextGenerationLLMs:
            _, created = LLM.objects.get_or_create(
                version=tp.name,
                defaults={"model": tp.value.model},
            )
            if created:
                logger.info(f"Loaded TextGenerationLLM '{tp.name}'.")
            else:
                logger.info(f"TextGenerationLLM '{tp.name}' already exists.")

    def _load_evaluators(self):
        for tp in Evaluators:
            _, created = Evaluator.objects.get_or_create(
                name=tp.name,
                defaults={"description": tp.value.description},
            )
            if created:
                logger.info(f"Loaded Evaluator '{tp.name}'.")
            else:
                logger.info(f"Evaluator '{tp.name}' already exists.")

    def handle(self, *args, **kwargs):
        logger.info("Loading TextPreprocessors...")
        self._load_preprocessors()
        logger.info("Finished loading TextPreprocessors.")

        logger.info("Loading TextProcessors...")
        self._load_processors()
        logger.info("Finished loading TextProcessors.")

        logger.info("Loading TextGenerationLLMs...")
        self._load_llms()
        logger.info("Finished loading TextGenerationLLMs.")

        logger.info("Loading Evaluators...")
        self._load_evaluators()
        logger.info("Finished loading Evaluators.")
