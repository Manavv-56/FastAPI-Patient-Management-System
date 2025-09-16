#!/bin/bash
# Demo startup script for Patient Management System
#
# This script starts both the FastAPI backend and Streamlit frontend.
# Run this from the project directory after activating your virtual environment.

echo "🏥 Starting Patient Management System Demo"
echo "==========================================="

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not detected. Please activate with:"
    echo "   source .venv/bin/activate"
    exit 1
fi

# Check if dependencies are installed
if ! python -c "import streamlit, requests, fastapi" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

echo "🚀 Starting FastAPI server on port 8000..."
uvicorn main:app --reload --port 8000 &
FASTAPI_PID=$!

# Wait a moment for FastAPI to start
sleep 3

echo "🌐 Starting Streamlit demo on port 8501..."
streamlit run streamlit_demo.py &
STREAMLIT_PID=$!

echo ""
echo "✅ Both servers are running!"
echo "   - FastAPI:  http://localhost:8000"
echo "   - FastAPI Docs:  http://localhost:8000/docs"
echo "   - Streamlit Demo:  http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop both servers..."

# Function to cleanup both processes
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $FASTAPI_PID 2>/dev/null
    kill $STREAMLIT_PID 2>/dev/null
    echo "✅ Cleanup complete!"
    exit 0
}

# Trap Ctrl+C
trap cleanup SIGINT

# Wait for user to stop
wait
