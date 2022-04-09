#!/bin/sh
script_file=`readlink -f "$0"`
script_dir=`dirname "$script_file"`
script_dir="$script_dir/app"
db_file='crashupload.db'
load_initialdata=0

admin_username="${ADMIN_USERNAME:-admin}"
admin_email="${ADMIN_EMAIL:-root@localhost}"
admin_password="${ADMIN_PASSWORD:-admin}"

if [ ! -d "$script_dir/data" ]; then
    mkdir "$script_dir/data"
fi

chmod 755 "$script_dir/data"

if [ ! -f "$script_dir/data/$db_file" ]; then
    load_initialdata=1
fi

if [ -f "$script_dir/data/$db_file" -a ! -s "$script_dir/data/$db_file" ]; then
    echo "remove empty DB file $script_dir/data/$db_file"
    rm "$script_dir/data/$db_file"
    load_initialdata=1
fi

python "$script_dir/manage.py" migrate --noinput
chown "$gunicorn_user" "$script_dir/data" "$script_dir/data/$db_file"

if [ $load_initialdata -ne 0 ]; then
    python "$script_dir/manage.py" loaddata "$script_dir/fixtures/crashdumpstate.json"

    DJANGO_SUPERUSER_PASSWORD="${admin_password}" python "$script_dir/manage.py" createsuperuser --noinput --username "${admin_username}" --email "${admin_email}"
fi

if [ ! -d "$script_dir/data/dumpdata" ]; then
    mkdir "$script_dir/data/dumpdata"
fi

# if [ ! -d "$script_dir/static" ]; then
#     mkdir "$script_dir/static"
# fi
# echo 'yes' | python "$script_dir/manage.py" collectstatic

chmod 755 "$script_dir/data/dumpdata"
