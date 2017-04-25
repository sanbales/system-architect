#!/usr/bin/env bash
rm system_architect/db.sqlite3
rm system_architect/system_architect/migrations/0*.py

python system_architect/manage.py makemigrations
python system_architect/manage.py makemigrations system_architect
python system_architect/manage.py migrate
python system_architect/manage.py migrate system_architect

if [ "$1" == full ]; then
  rm -rf _build/
  python system_architect/manage.py collectstatic
fi

python system_architect/manage.py add_fixture_data