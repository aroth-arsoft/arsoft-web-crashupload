#!/bin/sh
script_file=`readlink -f "$0"`
script_dir=`dirname "$script_file"`
gunicorn_user='app'
gunicorn_num_workers=${GUNICORN_NUM_WORKERS:-2}
gunicorn_num_threads=${GUNICORN_NUM_THREADS:-2}
gunicorn_debug=${GUNICORN_DEBUG:-0}
gunicorn_opts=''
db_file='crashupload.db'
load_initialdata=0

admin_username="${ADMIN_USERNAME:-admin}"
admin_email="${ADMIN_EMAIL:-root@localhost}"
admin_password="${ADMIN_PASSWORD:-admin}"

if [ $gunicorn_debug -ne 0 ]; then
    gunicorn_opts="$gunicorn_opts -R --capture-output --log-level=DEBUG"
fi

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

if [ ! -d "$script_dir/static" ]; then
    mkdir "$script_dir/static"
fi
echo 'yes' | python "$script_dir/manage.py" collectstatic

chmod 755 "$script_dir/data/dumpdata"
chown "$gunicorn_user" "$script_dir/data/dumpdata"

export PYTHONPATH='/app'

cat << EOF > /tmp/gunicorn.conf.py
secure_scheme_headers = {'X-FORWARDED-PROTOCOL': 'https', 'X-FORWARDED-PROTO': 'https', 'X-FORWARDED-SSL': 'on'}
EOF

exec gunicorn -c /tmp/gunicorn.conf.py --workers=${gunicorn_num_workers} --threads=${gunicorn_num_threads} $gunicorn_opts -b 0.0.0.0:8000 --user "$gunicorn_user" --group "nogroup" --chdir "$script_dir" app:application
exit $?

