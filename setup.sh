#!/bin/sh
# Instalar dependencias
echo "Instalar dependencias"
sudo dnf -y install python3 postgresql postgresql-server
# Dependencias de python
echo "Instalar requerimientos de python"
sudo pip3 install -r requirements.txt
echo "Iniciar el flask"
# Iniciar api
export FLASK_ENV=development
export FLASK_APP=run.py
export AUTHLIB_INSECURE_TRANSPORT=1
# Inicio del servidor
python3 -m flask initdb
python3 -m flask run
