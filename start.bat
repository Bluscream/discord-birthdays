@echo off
:: Windows Setup Script

@REM @"%SystemRoot%\System32\WindowsScriptHost\mshta.exe" http://chocolatey.org/install.ps1 %*
@REM choco install python git -y

python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt
python bot.py