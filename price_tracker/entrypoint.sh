#!/bin/bash

export PATH=$PATH:/home/price_tracker/.local/bin

export C_FORCE_ROOT=1
export DJANGO_LOG_LEVEL=INFO


if [ "$ENVIRONMENT" == "prod" ]; then
  echo "LOAD Production Environment"  
  python manage.py makemigrations --noinput
  python manage.py migrate --noinput
  python manage.py collectstatic --noinput

  exec gunicorn price_tracker.wsgi:application \
          --bind 0.0.0.0:8080 \
          --workers 2 \
          --access-logfile -
elif [ "$ENVIRONMENT" == "dev" ]; then
  echo "LOAD Development Environment"
  /bin/bash
else
  echo "unknown environment"
  /bin/bash
fi


