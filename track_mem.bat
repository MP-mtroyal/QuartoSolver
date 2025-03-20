@echo off
setlocal EnableDelayedExpansion
set max_memory=0

echo Tracking Python memory usage... Press Ctrl+C to stop.
echo --------------------------------------------

:loop
set current_memory=0

for /f "tokens=5 delims= " %%A in ('tasklist /FI "IMAGENAME eq python.exe" ^| find "python.exe"') do (
    set mem=%%A
    set mem=!mem:,=!  REM Remove commas in case of large numbers
    set /a current_memory=!mem!
    if !current_memory! GTR !max_memory! set max_memory=!current_memory!
)

echo Current: !current_memory! KB ^| Max^: !max_memory! KB

timeout /t 1 >nul
goto loop