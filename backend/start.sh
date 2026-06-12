#!/bin/bash

# Wait for DB to be healthy (optional, docker-compose depends_on healthcheck handles this usually)
echo "Waiting for database to be ready..."

# Run migrations
echo "Running database migrations..."
python -m alembic upgrade head

# Run seed script
echo "Seeding database..."
python seeds/seed.py

# Start the application
echo "Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
