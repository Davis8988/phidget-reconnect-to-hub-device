@echo off
setlocal EnableDelayedExpansion

set nssmExe_x64=%~dp0nssm.exe
set nssm=%nssmExe_x64%

set phidgetHubRelaySwitchAlwaysOn_Name=PhidgetHubRelaySwitchAlwaysOn

echo Uninstall "%phidgetHubRelaySwitchAlwaysOn_Name%" as a service
CHOICE /C YN /M "Are you sure"
if %errorlevel% equ 2 echo Aborting.. && exit 0

:: Remove old service if exist
echo Removing service: "%phidgetHubRelaySwitchAlwaysOn_Name%"
if not exist "%nssmExe_x64%" (
	echo. 
	sc stop "%phidgetHubRelaySwitchAlwaysOn_Name%"
	sc delete "%phidgetHubRelaySwitchAlwaysOn_Name%"
) else (
	"%nssm%" status "%phidgetHubRelaySwitchAlwaysOn_Name%"
	if !errorlevel! equ 0 (
		echo Stopping service: "%phidgetHubRelaySwitchAlwaysOn_Name%" 
		"%nssm%" stop "%phidgetHubRelaySwitchAlwaysOn_Name%"
		timeout /t 2 > nul
		echo Removing service: "%phidgetHubRelaySwitchAlwaysOn_Name%"
		"%nssm%" remove "%phidgetHubRelaySwitchAlwaysOn_Name%" confirm

	)
)

echo.
echo OK. Service is uninstalled
echo.
echo Finished uninstalling %phidgetHubRelaySwitchAlwaysOn_Name% service
echo.
echo Done
echo.

timeout /t 10