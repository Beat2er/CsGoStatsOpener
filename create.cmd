@echo off
venv\Scripts\pyinstaller.exe --icon=image.ico -F main.py
copy dist\main.exe CsGoStatsOpener.exe
rmdir dist /s /q
rmdir build /s /q