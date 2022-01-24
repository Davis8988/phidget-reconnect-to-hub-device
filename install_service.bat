@echo off

set nssmExe_x64=%~dp0nssm.exe
set nssm=%nssmExe_x64%

set installDir=C:\PhidgetHubRelaySwitchAlwaysOn
set phidgetHubRelaySwitchAlwaysOn_Name=PhidgetHubRelaySwitchAlwaysOn
set phidgetHubRelaySwitchAlwaysOn_DisplayName=PhidgetHubRelaySwitchAlwaysOn
set phidgetHubRelaySwitchAlwaysOn_ExeName=PhidgetHubRelaySwitchAlwaysOn.exe
set phidgetHubRelaySwitchAlwaysOn_ExePath=%~dp0%phidgetHubRelaySwitchAlwaysOn_ExeName%
set phidgetHubRelaySwitchAlwaysOn_ConfigFileName=prometheus.yml

:: Check params
if not exist "%nssmExe_x64%" echo. && echo Error - Nssm exe file doesn't exist or is unreachable at: "%nssmExe_x64%" && pause && exit 1
if not exist "%phidgetHubRelaySwitchAlwaysOn_ExePath%" echo. && echo Error - Exe File or is unreachable at: "%phidgetHubRelaySwitchAlwaysOn_ExePath%" && pause && exit 1

echo Install "%phidgetHubRelaySwitchAlwaysOn_Name%" as a service
CHOICE /C YN /M "Are you sure"
if %errorlevel% equ 2 echo Aborting.. && exit 0

:: Remove old service if exist
echo Removing old service if exist..
"%nssm%" status "%phidgetHubRelaySwitchAlwaysOn_Name%"
if %errorlevel% equ 0 (
	echo Stopping service: "%phidgetHubRelaySwitchAlwaysOn_Name%" 
	"%nssm%" stop "%phidgetHubRelaySwitchAlwaysOn_Name%"
	timeout /t 2 > nul
	echo Removing service: "%phidgetHubRelaySwitchAlwaysOn_Name%"
	"%nssm%" remove "%phidgetHubRelaySwitchAlwaysOn_Name%" confirm

)

:: Kill running processes
echo Stopping any running processes of %phidgetHubRelaySwitchAlwaysOn_Name%
tasklist | find /i "%phidgetHubRelaySwitchAlwaysOn_ExeName%" && taskkill /im "%phidgetHubRelaySwitchAlwaysOn_ExeName%" /t /f
tasklist | find /i "%phidgetHubRelaySwitchAlwaysOn_ExeName%" && echo. && echo Error - Failed stopping running process: "%phidgetHubRelaySwitchAlwaysOn_ExeName%" && echo Please kill it manually and re-execute this script && pause && exit 1

:: Copy files to install dir
echo Preparing to copy files to install dir: %installDir%
if not exist "%installDir%" echo Creating dir: "%installDir%" && mkdir "%installDir%"
if not exist "%installDir%" echo. && echo Error - Failed to create dir: "%installDir%" && echo Please create manually and re-execute this script && pause && exit 1

:: Remove old version exe file
if exist "%installDir%\%phidgetHubRelaySwitchAlwaysOn_ExeName%" echo Removing old version exe: "%installDir%\%phidgetHubRelaySwitchAlwaysOn_ExeName%" && del /q "%installDir%\%phidgetHubRelaySwitchAlwaysOn_ExeName%"
if exist "%installDir%\%phidgetHubRelaySwitchAlwaysOn_ExeName%" echo. && echo Error  -Failed removing old version exe file: "%installDir%\%phidgetHubRelaySwitchAlwaysOn_ExeName%" && echo Please remove it manually and re-execute this script && pause && exit 1

:: Copy new version exe
echo Copying: "%phidgetHubRelaySwitchAlwaysOn_ExePath%" to: "%installDir%\%phidgetHubRelaySwitchAlwaysOn_ExeName%"
copy /y "%phidgetHubRelaySwitchAlwaysOn_ExePath%" "%installDir%\%phidgetHubRelaySwitchAlwaysOn_ExeName%"
if %errorlevel% neq 0 echo. && echo WARNING: Seems like copy command failed to work..
if not exist "%installDir%\%phidgetHubRelaySwitchAlwaysOn_ExeName%" echo. && echo Error - Failed copying from: "%phidgetHubRelaySwitchAlwaysOn_ExePath%" to: "%installDir%\%phidgetHubRelaySwitchAlwaysOn_ExeName%" && pause && exit 1

:: Install as a service
echo Installing %phidgetHubRelaySwitchAlwaysOn_Name% as a service
echo Creating new service "%phidgetHubRelaySwitchAlwaysOn_Name%"
echo Executing: "%nssm%" install "%phidgetHubRelaySwitchAlwaysOn_Name%" "%phidgetHubRelaySwitchAlwaysOn_ExePath%"
"%nssm%" install "%phidgetHubRelaySwitchAlwaysOn_Name%" "%phidgetHubRelaySwitchAlwaysOn_ExePath%"
if %errorlevel% neq 0 echo. && echo Error - Failed creating new service: "%phidgetHubRelaySwitchAlwaysOn_Name%" && pause && exit 1

echo Configuring %phidgetHubRelaySwitchAlwaysOn_Name% Service..
"%nssm%" set "%phidgetHubRelaySwitchAlwaysOn_Name%" AppStdout "%installDir%\service_std_out.log"
"%nssm%" set "%phidgetHubRelaySwitchAlwaysOn_Name%" AppStdoutCreationDisposition 2
"%nssm%" set "%phidgetHubRelaySwitchAlwaysOn_Name%" AppStderr "%installDir%\service_std_err.log"
"%nssm%" set "%phidgetHubRelaySwitchAlwaysOn_Name%" AppStderrCreationDisposition 2
"%nssm%" set "%phidgetHubRelaySwitchAlwaysOn_Name%" DisplayName "%phidgetHubRelaySwitchAlwaysOn_DisplayName%"
"%nssm%" set "%phidgetHubRelaySwitchAlwaysOn_Name%" AppExit Default Restart
"%nssm%" set "%phidgetHubRelaySwitchAlwaysOn_Name%" AppRestartDelay 5000
"%nssm%" set "%phidgetHubRelaySwitchAlwaysOn_Name%" Start SERVICE_DELAYED_AUTO_START 

echo Starting the %phidgetHubRelaySwitchAlwaysOn_Name% service:
"%nssm%" restart "%phidgetHubRelaySwitchAlwaysOn_Name%"
if %errorlevel% neq 0 echo. && echo Error - Failed starting service: "%phidgetHubRelaySwitchAlwaysOn_Name%" && echo Service is still not running.. && pause && exit 1

echo.
echo OK. Service is running
echo.
echo Finished installing %phidgetHubRelaySwitchAlwaysOn_Name% service
echo.
echo Done
echo.

timeout /t 10