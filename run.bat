@echo off
title OS Algorithm Visualizer
echo ======================================================
echo          Starting OS Algorithm Visualizer
echo ======================================================
echo.

python desktop.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Application exited with error code %ERRORLEVEL%.
    pause
)
