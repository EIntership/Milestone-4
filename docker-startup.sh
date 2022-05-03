#!/bin/bash
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
# python manage.py collectstatic --noinput

#if [ -z "$MANAGE_COMMAND" ]
#then
#if [ "$MANAGE_PY" = "True" ]; then
#  echo "Start manage.py"
#  python manage.py runserver ${GUNICORN_BIND} --noreload
#else
#  echo "Start GUNICORN"
#fi
#else
#      echo "Start $MANAGE_COMMAND command"
#      python manage.py ${MANAGE_COMMAND}
#fi
