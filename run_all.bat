@echo off
REM Runs the three verification scripts for the 3x3x3 DR Code paper.
setlocal

where python >nul 2>&1
if errorlevel 1 (
  echo Python was not found on PATH. Install Python 3.9 or later and try again.
  exit /b 1
)

echo ============================================================
echo  1/3  verify_3d_recovery.py
echo ============================================================
python verify_3d_recovery.py
if errorlevel 1 goto failed

echo.
echo ============================================================
echo  2/3  verify_3d_group.py
echo ============================================================
python verify_3d_group.py
if errorlevel 1 goto failed

echo.
echo ============================================================
echo  3/3  verify_3d_round2.py
echo ============================================================
python verify_3d_round2.py
if errorlevel 1 goto failed

echo.
echo All verification scripts completed successfully.
pause
exit /b 0

:failed
echo.
echo A verification script reported a failure.
pause
exit /b 1
