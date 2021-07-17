@echo off
venv\Scripts\pyinstaller.exe main.py
copy dist\main\main.exe CsGoStatsOpener.exe
rmdir dist /s /q
rmdir build /s /q