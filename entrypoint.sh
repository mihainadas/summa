#!/bin/sh
set -e
python manage.py migrate --noinput
python manage.py core_create_superuser
python manage.py core_load_summa
exec gunicorn -w 4 -b 0.0.0.0:8000 galandriel.wsgi:application