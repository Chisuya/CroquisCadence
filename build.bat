@echo off
echo ================================================
echo Building CroquisCadence.exe
echo ================================================
echo.

echo Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Building executable (this may take a few minutes)...
pyinstaller CroquisCadence.spec

echo.
echo ================================================
echo Build Complete!
echo ================================================
echo.
echo Your application is in: dist\CroquisCadence\
echo.
echo To distribute:
echo 1. Go to dist\CroquisCadence\
echo 2. Add your reference images to test_data\references\
echo 3. Add sound files to assets\ folder (optional)
echo 4. Zip the entire CroquisCadence folder
echo 5. Share with artists!
echo.
pause
