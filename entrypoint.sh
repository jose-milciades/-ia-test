#!/bin/bash

python3 set_env_variable_port.py

source port_env_variable.txt
echo $FLASK_PORT

sleep 1

#uwsgi app.ini
#gunicorn -w 1 --threads=4 -t 0 -b 0.0.0.0:$FLASK_PORT run:app
python3 run.py

exec "$@"