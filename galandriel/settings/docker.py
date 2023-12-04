import os
import dj_database_url
from decouple import config
from .base import *

DATABASES = {
    "default": dj_database_url.config(default=config("DATABASE_URL"), conn_max_age=60)
}

DEBUG = False

LOGGING["handlers"]["file"]["level"] = "WARNING"
LOGGING["loggers"]["django"]["level"] = "WARNING"
