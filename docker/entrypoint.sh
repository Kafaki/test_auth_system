#!/bin/sh
set -e

until nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  sleep 0.5
done
echo " Postgres доступен"

python manage.py migrate --noinput


python manage.py loaddata core/fixtures/core_data.json || true
python manage.py create_test_users || true

echo " Запуск Django dev-сервера..."
python manage.py runserver 0.0.0.0:8000
