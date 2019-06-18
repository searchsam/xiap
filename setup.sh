#!/bin/sh
# Instalar dependencias
echo "Instalar dependencias"
sudo dnf -y install python3 sqlite
# Dependencias de python
echo "Instalar requerimientos de python"
pip3 install -r requirements.txt --user
echo "Iniciar el flask"
# Iniciar api
# export AUTHLIB_INSECURE_TRANSPORT=1
python3 -m flask initdb
python3 run.py
