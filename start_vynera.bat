@echo off
title VYNERA AI Server
cd /d "D:\myprojects\Companion\VYNERA AI"
echo.
echo  ██╗   ██╗██╗   ██╗███╗   ██╗███████╗██████╗  █████╗ 
echo  ██║   ██║╚██╗ ██╔╝████╗  ██║██╔════╝██╔══██╗██╔══██╗
echo  ██║   ██║ ╚████╔╝ ██╔██╗ ██║█████╗  ██████╔╝███████║
echo  ╚██╗ ██╔╝  ╚██╔╝  ██║╚██╗██║██╔══╝  ██╔══██╗██╔══██║
echo   ╚████╔╝    ██║   ██║ ╚████║███████╗██║  ██║██║  ██║
echo    ╚═══╝     ╚═╝   ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝
echo.
echo  Starting VYNERA AI server...
echo  Open browser: http://127.0.0.1:8000
echo  Press CTRL+C to stop
echo ════════════════════════════════════════════════════════
echo.
"d:/myprojects/Companion/VYNERA AI/venv/Scripts/python.exe" app.py
echo.
echo  Server stopped. Press any key to close.
pause