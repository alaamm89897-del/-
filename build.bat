@echo off
echo Building Recruitmentify application with main.py as the entry point...
echo.

rem Activate virtual environment if you have one
rem call .venv\Scripts\activate

rem Install PyInstaller if not already installed
pip install pyinstaller

rem Run PyInstaller with the spec file
pyinstaller --clean recruitmentify.spec

echo.
echo Build completed. Your application now starts with main.py as the entry point.
echo Check the 'dist' folder for your executable.
pause
