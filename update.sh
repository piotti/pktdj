#!/bin/bash
git pull
python3.6 manage.py makemigrations dj
python3.6 manage.py migrate
sh ./move_static.sh
../apache2/bin/restart
