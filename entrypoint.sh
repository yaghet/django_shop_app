#!/bin/sh
set -e

uv run manage.py migrate
uv run manage.py loaddata --exclude=contenttypes fixtures/fixtures.json

exec uv run manage.py runserver 0.0.0.0:8000
