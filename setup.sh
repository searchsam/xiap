#!/bin/sh
sudo apt install python3-virtualenv
python3 -m venv venv
source venv/bin/activate
pip freeze > requirements.txt
export FLASK_APP=run.py
python -m flask run --host=0.0.0.0
