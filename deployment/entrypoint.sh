#!/usr/bin/env sh
set -e

WORKER_CLASS=uvicorn.workers.UvicornWorker
alembic upgrade heads
exec gunicorn src.main:app \
  --name $NAME \
  --workers $WORKERS \
  --worker-class $WORKER_CLASS \
  --user=app \
  --group=app \
  --bind=0.0.0.0:$PORT \
  --log-level=$LOG_LEVEL \
"$@"
