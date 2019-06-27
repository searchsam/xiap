#!/bin/sh
# Instalar dependencias
echo "Instalar dependencias"
sudo dnf -y install python3 sqlite
# Dependencias de python
echo "Instalar requerimientos de python"
sudo pip3 install -r requirements.txt
echo "Iniciar el flask"
# Iniciar api
export FLASK_APP=run.py
export AUTHLIB_INSECURE_TRANSPORT=1
python3 -m flask initdb
python3 -m flask run
