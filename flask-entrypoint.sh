#!/usr/bin/env bash
  set -e
  echo "Waiting for mysql ready..."
  while ! </dev/tcp/db/3306; do
     echo "MySQL not ready - sleeping..."
     sleep 5
  done
  echo "MySQL ready!"

  # Load environment variables
  set -a  # Auto-export variables
  source .env  # Load from .env
  #set +a

  sleep 2
  
  # Initialize migrations if needed
  if [ -d "migrations" ] && [ "$(ls -A migrations)" ]; then
    echo "Migrations exist, skipping init..."
  else
    flask db init
  fi
  flask db migrate -m 'create initial tables'
  flask db upgrade
  
  #API_HOST="dnevnik" 

  # Create initial users using env vars
  echo "Creating initial users..."

echo "Cleaning passwords from CRLF..."
DNEVNIK_TEACHER_PASS=$(echo -n "$DNEVNIK_TEACHER_PASS" | tr -d '\r')
DNEVNIK_STUDENT_PASS=$(echo -n "$DNEVNIK_STUDENT_PASS" | tr -d '\r')
DNEVNIK_ADMIN_PASS=$(echo -n "$DNEVNIK_ADMIN_PASS" | tr -d '\r')

echo "Creating initial users with clean passwords..."
flask create-user teacher1 "$DNEVNIK_TEACHER_PASS" teacher || true
flask create-user teacher2 "$DNEVNIK_TEACHER_PASS" teacher || true
flask create-user student1 "$DNEVNIK_STUDENT_PASS" student || true
flask create-user student2 "$DNEVNIK_STUDENT_PASS" student || true  
flask create-user admin "$DNEVNIK_ADMIN_PASS" admin || true

exec  flask run --host 0.0.0.0 --port 5000
  
