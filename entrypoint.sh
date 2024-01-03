#!/bin/sh
set -e
python manage.py migrate --noinput
python manage.py core_create_superuser
python manage.py core_load_summa
python manage.py process_tasks > django-background-tasks.log &
exec gunicorn -w 4 -b 0.0.0.0:8000 galandriel.wsgi:application