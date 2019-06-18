# Importar las dependencias de flask
from flask import Blueprint, redirect, url_for

# Definir el blueprint: 'inicio', establecer el prefijo de la url: app.url/inico
mod_inicio = Blueprint('inicio', __name__)


@mod_inicio.route('/', methods=['GET', 'POST'])
def raiz():
    return redirect(url_for('curia.inicio'))
