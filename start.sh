#!/bin/bash

# ChilliDoc AI - Linux/Mac Startup Script

echo "========================================"
echo "ChilliDoc AI - Startup Script"
echo "========================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ first"
    exit 1
fi

echo "[1/4] Python detected"
echo ""

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "[2/4] Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created successfully"
else
    echo "[2/4] Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "[3/4] Activating virtual environment..."
source venv/bin/activate
echo ""

# Install dependencies
echo "[4/4] Installing dependencies..."
echo "This may take a few minutes..."
pip install -r requirements_web.txt --quiet
echo "Dependencies installed successfully"
echo ""

# Check for model file
if [ ! -f "best_chilli_disease_model.h5" ] && [ ! -f "chilli_disease_detection_model_final.h5" ] && [ ! -f "chilli_disease_detection_model_final.keras" ]; then
    echo "WARNING: No model file found!"
    echo "Please ensure you have trained the model first using the Jupyter notebook."
    echo "Looking for one of these files:"
    echo "  - best_chilli_disease_model.h5"
    echo "  - chilli_disease_detection_model_final.h5"
    echo "  - chilli_disease_detection_model_final.keras"
    echo ""
    read -p "Press Enter to continue or Ctrl+C to exit..."
fi

echo "========================================"
echo "Starting ChilliDoc AI Server..."
echo "========================================"
echo ""
echo "Server will start at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""
echo "========================================"
echo ""

# Start the Flask application
python app.py

# Deactivate virtual environment on exit
deactivate
