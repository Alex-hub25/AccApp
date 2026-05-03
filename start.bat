@echo off
setlocal

echo === AccApp Local Dev Startup ===

:: Check PostgreSQL service
sc query postgresql-17 >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] PostgreSQL service "postgresql-17" not found. Skipping.
) else (
    sc query postgresql-17 | findstr /i "RUNNING" >nul 2>&1
    if %errorlevel% neq 0 (
        echo [INFO] Starting PostgreSQL service...
        net start postgresql-17
        if %errorlevel% neq 0 (
            echo [ERROR] Failed to start PostgreSQL. Try running this script as Administrator.
            pause
            exit /b 1
        )
    ) else (
        echo [OK] PostgreSQL is already running.
    )
)

:: Activate virtual environment
set VENV=%~dp0venv\Scripts\activate.bat
if not exist "%VENV%" (
    echo [ERROR] Virtual environment not found at %VENV%
    pause
    exit /b 1
)
call "%VENV%"

:: Run Django dev server
echo [INFO] Starting Django development server...
cd /d "%~dp0backend"
"%~dp0venv\Scripts\python.exe" manage.py runserver

endlocal
