import os
import dj_database_url
from decouple import config
from .base import *

DATABASES = {
    "default": dj_database_url.parse(config("DATABASE_URL_LOCAL"), conn_max_age=60)
}
