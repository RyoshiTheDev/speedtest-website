#!/bin/bash
PORT=${PORT:-5000}
echo "Starting on port $PORT"
gunicorn web_app_official:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile -
