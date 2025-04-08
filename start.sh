#!/bin/bash
# Linux Setup Script

# sudo apt update
# sudo apt install -y python3 python3-pip python3-venv git

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python bot.py