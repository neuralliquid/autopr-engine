@echo off
REM Batch file to run the comprehensive LLM provider test suite
REM Usage: test_llm_providers.bat

echo.
echo ========================================
echo   AutoPR LLM Provider Test Suite
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Run the test suite
echo Running comprehensive LLM provider tests...
echo.

python test_llm_providers.py

REM Check exit code and provide feedback
if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   Tests completed successfully!
    echo ========================================
) else (
    echo.
    echo ========================================
    echo   Some tests failed. Check output above.
    echo ========================================
)

echo.
echo Press any key to exit...
pause >nul
