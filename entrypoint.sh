#!/bin/sh
set -e
python manage.py migrate --noinput
exec gunicorn -w 4 -b 0.0.0.0:8000 galandriel.wsgi:application