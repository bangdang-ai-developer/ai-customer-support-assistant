#!/bin/bash

# Railway startup script for BIWOCO AI Backend

echo "Starting BIWOCO AI Customer Support Assistant Backend..."

# Set working directory
cd /app

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Create database tables if they don't exist
echo "Creating database tables..."
python -c "
from app.core.database import engine, Base
from app.models import user, conversation, knowledge, scenario, message
Base.metadata.create_all(bind=engine)
print('Database tables created successfully')
"

# Start the FastAPI server
echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT