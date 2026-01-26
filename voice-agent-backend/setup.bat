@echo off
REM Setup script for voice-agent-backend (Windows)
REM This script creates a virtual environment and installs dependencies

echo 🚀 Setting up voice-agent-backend...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.9 or higher.
    exit /b 1
)

REM Create virtual environment
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ℹ️  Virtual environment already exists
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

echo.
echo ✅ Setup complete!
echo.
echo To activate the virtual environment, run:
echo   venv\Scripts\activate
echo.
echo To deactivate, run:
echo   deactivate
echo.
echo Next steps:
echo 1. Copy .env.example to .env and fill in your API keys
echo 2. Set up your Supabase database (see README.md)
echo 3. Run: python run.py dev

pause
