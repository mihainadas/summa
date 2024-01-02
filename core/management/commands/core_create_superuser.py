import logging
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decouple import config

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Create a superuser based on defined SU_ variables, if one does not exist"

    def handle(self, *args, **kwargs):
        try:
            su_username = config("SU_USERNAME")
            su_email = config("SU_EMAIL")
            su_password = config("SU_PASSWORD")
        except Exception:
            logger.error("SU_USERNAME, SU_EMAIL, or SU_PASSWORD not set.")
            return
        User = get_user_model()
        if not User.objects.filter(username=su_username).exists():
            logger.info(f"Superuser '{su_username}' not found. Creating one...")
            logger.info("Checking if SU_USERNAME, SU_EMAIL, and SU_PASSWORD are set...")
            User.objects.create_superuser(su_username, su_email, su_password)
            logger.info("Superuser created.")

        else:
            logger.info(f"Superuser '{su_username}' already exists.")
