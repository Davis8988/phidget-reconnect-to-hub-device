@echo off

 

rem By David Yair <david.yair@elbitsystems.com>

 

rem Vars
set pythonScriptName=PhidgetHubRelaySwitchAlwaysOn
set iconFile=%~dp0Icons\%pythonScriptName%.ico
set outputDir=%~dp0Exe
set pythonScriptFilePath=%~dp0%pythonScriptName%.py
set pyinstallerArgs=-i "%iconFile%" --distpath "%outputDir%" --name "%pythonScriptName%" --console --onefile --noconfirm --clean "%pythonScriptFilePath%"

 

rem Check pyinstaller
where pyinstaller
if %errorlevel% neq 0 echo Error - Cannot compile your script to an exe without 'pyinstaller.exe' in the path variable of this machine && echo Install it by executing: 'pip install pyinstaller' && pause && exit 1

 
rem Ask before continuing
CHOICE /C YN /M "Do you want to compile %pythonScriptName%.py to an exe?"
if %errorlevel% equ 2 exit 0

 
REM Compile
echo Compiling..
pyinstaller %pyinstallerArgs%
if %errorlevel% neq 0 echo Error - Failed to compile %pythonScriptName%.py to an exe file && pause && exit 1

 
REM Clean up
echo Cleaning..
if exist "%~dp0build" rmdir /q /s "%~dp0build"
if exist "%~dp0__pycache__" rmdir /q /s "%~dp0__pycache__"
if exist "%~dp0%pythonScriptName%.spec" del /q "%~dp0%pythonScriptName%.spec"

 
rem Finish
echo.
echo Finished compiling successfully
echo.
 

timeout 3