#!/bin/sh
script_file=`readlink -f "$0"`
script_dir=`dirname "$script_file"`
gunicorn_user='app'
gunicorn_num_workers=${GUNICORN_NUM_WORKERS:-2}
gunicorn_num_threads=${GUNICORN_NUM_THREADS:-2}
gunicorn_debug=${GUNICORN_DEBUG:-0}
gunicorn_opts=''
db_file='crashupload.db'

if [ $gunicorn_debug -ne 0 ]; then
    gunicorn_opts="$gunicorn_opts -R --capture-output --log-level=DEBUG"
fi

if [ ! -d "$script_dir/data" ]; then
    mkdir "$script_dir/data"
fi

chmod 755 "$script_dir/data"

if [ -f "$script_dir/data/$db_file" -a ! -s "$script_dir/data/$db_file" ]; then
    echo "remove empty DB file $script_dir/data/$db_file"
    rm "$script_dir/data/$db_file"
fi

python "$script_dir/manage.py" migrate --noinput
chown "$gunicorn_user" "$script_dir/data" "$script_dir/data/$db_file"

if [ ! -d "$script_dir/data/dumpdata" ]; then
    mkdir "$script_dir/data/dumpdata"
fi

chmod 755 "$script_dir/data/dumpdata"
chown "$gunicorn_user" "$script_dir/data/dumpdata"

export PYTHONPATH='/app'

exec gunicorn --workers=${gunicorn_num_workers} --threads=${gunicorn_num_threads} $gunicorn_opts -b 0.0.0.0:8000 --user "$gunicorn_user" --group "nogroup" --chdir "$script_dir" app:application
exit $?

