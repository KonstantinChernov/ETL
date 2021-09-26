#!/bin/bash

python3 manage.py migrate admin --no-input
python3 manage.py migrate auth --no-input
python3 manage.py migrate contenttypes --no-input
python3 manage.py migrate sessions --no-input

python3 manage.py migrate

python3 manage.py collectstatic --no-input

exec gunicorn config.wsgi:application -b 0.0.0.0:8000 --reload
