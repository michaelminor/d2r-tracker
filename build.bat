@echo off
echo Installing PyInstaller if needed...
python -m pip install pyinstaller --quiet

echo.
echo Building D2RTracker.exe...
python -m PyInstaller --onefile --windowed --name "D2RTracker" d2r_tracker.py

echo.
echo Done! Your .exe is in the dist\ folder.
echo Copy D2RTracker.exe wherever you like. config.json will be created next to it on first run.
pause
