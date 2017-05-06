#!/usr/bin/env bash
sqlitedb_file="system_architect/db.sqlite3"
if [ -f "$sqlitedb_file" ]
then
	rm "$sqlitedb_file"
	echo "Deleted '$sqlitedb_file'"
else
    echo "Could not find '$sqlitedb_file'"
fi

echo "Deleting these migration folders:" `find -type d -name migrations`
rm -rf `find -type d -name migrations`

python system_architect/manage.py makemigrations system_architect
python system_architect/manage.py migrate

if [ "$1" == full ]; then
  rm -rf _build/
  python system_architect/manage.py collectstatic
fi

python system_architect/manage.py add_fixture_data