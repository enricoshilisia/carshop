#!/usr/bin/env bash
# Django deploy on the cPanel host (run over SSH). Frontend deploys separately.
set -euo pipefail
cd ~/backend
git pull
~/venv/bin/pip install -r requirements.txt
~/venv/bin/python manage.py migrate --noinput
~/venv/bin/python manage.py collectstatic --noinput
mkdir -p tmp && touch tmp/restart.txt   # Passenger restart
