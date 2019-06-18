#!/bin/sh
sudo apt install python3-virtualenv
python3 -m venv venv
source venv/bin/activate
pip freeze > requirements.txt
python run.py
