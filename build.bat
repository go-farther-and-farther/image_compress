@echo off
pushd "%~dp0"
pip install pyinstaller
pyinstaller --onefile --clean image_compress.py
copy image_compress_config.json dist\
echo.
echo Done.
pause
