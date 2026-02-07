#!/bin/bash
# Todo App Deployment Script - Built by Sparky

echo "🚀 Deploying Sparky Todo App..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is not installed"
    exit 1
fi

echo "✓ Node.js $(node --version) detected"
echo "✓ npm $(npm --version) detected"

# Install backend dependencies
echo ""
echo "📦 Installing backend dependencies..."
cd backend
npm install --quiet

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"

# Start server
echo ""
echo "🎯 Starting Todo API server..."
echo ""
echo "======================================"
echo "  Todo App is now running!"
echo "======================================"
echo ""
echo "  Frontend: http://localhost:3000"
echo "  API:      http://localhost:3000/api/todos"
echo "  Health:   http://localhost:3000/api/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

node server.js
