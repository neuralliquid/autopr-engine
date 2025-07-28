@echo off
REM Code Quality Management Script for AutoPR Engine (Windows)
REM This batch file provides convenient commands for running code quality tools

setlocal enabledelayedexpansion

REM Change to project root directory
cd /d "%~dp0\.."

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    exit /b 1
)

REM Parse command line arguments
if "%1"=="" (
    goto :help
)

if "%1"=="format" goto :format
if "%1"=="lint" goto :lint
if "%1"=="test" goto :test
if "%1"=="security" goto :security
if "%1"=="pre-commit" goto :pre_commit
if "%1"=="check" goto :check
if "%1"=="install" goto :install_hooks
goto :help

:format
echo 🔄 Formatting code...
python -m black . --line-length 100
if errorlevel 1 goto :error
python -m isort . --profile black
if errorlevel 1 goto :error
echo ✅ Code formatting completed
goto :end

:lint
echo 🔄 Running linting tools...
echo Running flake8...
python -m flake8 . --max-line-length 100
echo Running mypy...
python -m mypy . --config-file pyproject.toml
echo Running bandit...
python -m bandit -r . -c pyproject.toml
echo ✅ Linting completed
goto :end

:test
echo 🔄 Running test suite...
python -m pytest -v --cov=autopr --cov-report=term-missing
if errorlevel 1 goto :error
echo ✅ Tests completed
goto :end

:security
echo 🔄 Checking dependencies for security vulnerabilities...
python -m safety check
echo ✅ Security check completed
goto :end

:pre_commit
if "%2"=="install" goto :install_hooks
if "%2"=="run" goto :run_hooks
echo Usage: %0 pre-commit [install^|run]
goto :end

:install_hooks
echo 🔄 Installing pre-commit hooks...
python -m pre_commit install
if errorlevel 1 goto :error
python -m pre_commit install --hook-type commit-msg
if errorlevel 1 goto :error
echo ✅ Pre-commit hooks installed
goto :end

:run_hooks
echo 🔄 Running pre-commit hooks...
python -m pre_commit run --all-files
echo ✅ Pre-commit hooks completed
goto :end

:check
echo 🚀 Running full code quality check...
echo.
call :format
echo.
call :lint
echo.
call :test
echo.
call :security
echo.
echo 🎉 Full code quality check completed!
goto :end

:help
echo AutoPR Engine Code Quality Management
echo.
echo Usage: %0 [command]
echo.
echo Commands:
echo   format      Format code with black and isort
echo   lint        Run linting tools (flake8, mypy, bandit)
echo   test        Run test suite
echo   security    Check dependencies for vulnerabilities
echo   pre-commit  Pre-commit commands:
echo     install   Install pre-commit hooks
echo     run       Run pre-commit hooks
echo   check       Run all code quality checks
echo   install     Install pre-commit hooks (shortcut)
echo.
echo Examples:
echo   %0 format
echo   %0 lint
echo   %0 test
echo   %0 check
echo   %0 pre-commit install
goto :end

:error
echo ❌ Command failed with error code %errorlevel%
exit /b %errorlevel%

:end
endlocal
