@echo off
set SNOCS_ERRORLEVEL=

if "%OS%" == "Windows_NT" goto WinNT
echo NOT WINDOW NT SO UNDEFINED BEHAVIOUR YET


:WinNT
set scriptname=%~dp0%~n0
python "%scriptname%" %*
