@echo off

@REM @"%SystemRoot%\System32\WindowsScriptHost\mshta.exe" http://chocolatey.org/install.ps1 %*
@REM choco install python git -y
python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install --upgrade -r requirements.txt
python __main__.py