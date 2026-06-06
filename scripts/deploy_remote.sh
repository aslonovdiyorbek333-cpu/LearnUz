#!/usr/bin/env bash
set -e

BRANCH=${1:-main}
REMOTE=${2:-origin}
REPO_PATH=${3:-~/LearnUz_prj}
VENV=${4:-/home/$USER/.virtualenvs/venv}

if [ -z "$PA_USER" ]; then
  echo "Please set PA_USER environment variable to your PythonAnywhere username (export PA_USER=yourusername)"
  exit 1
fi

echo "Deploying branch $BRANCH from $REMOTE to $REPO_PATH using venv $VENV"

ssh "$PA_USER@ssh.pythonanywhere.com" "cd $REPO_PATH && source $VENV/bin/activate && git pull $REMOTE $BRANCH && pip install -r requirements.txt && python manage.py migrate --noinput && python manage.py collectstatic --noinput && touch /var/www/${PA_USER}_pythonanywhere_com_wsgi.py"

echo "Remote deploy finished."
