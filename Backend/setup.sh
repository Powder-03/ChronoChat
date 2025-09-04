#!/bin/bash

# ChronoChat Backend Setup Script

echo "🚀 Setting up ChronoChat Backend..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is required but not installed."
    exit 1
fi

# Check if Redis is installed
if ! command -v redis-cli &> /dev/null; then
    echo "❌ Redis is required but not installed."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📋 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating environment file..."
    cp .env.example .env
    echo "⚠️  Please update the .env file with your configurations"
fi

# Create database if it doesn't exist
echo "🗄️  Setting up database..."
createdb chronochat 2>/dev/null || echo "Database 'chronochat' already exists or couldn't be created"

echo "✅ Backend setup complete!"
echo ""
echo "Next steps:"
echo "1. Update your .env file with proper configurations"
echo "2. Start Redis server: redis-server"
echo "3. Start the application: uvicorn main:app --reload"
echo "4. Visit http://localhost:8000/docs for API documentation"
