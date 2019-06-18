# importar flask y los operadores de plantilla
from flask import Flask, render_template

# Definir la aplicacion del objeto WSGI
app = Flask(__name__)

# Configuraciones
app.config.from_object('config')

# Ejemplo de manejo de error HTTP
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

# Importar a modulo / componente usando la variable de manejo blueprint (mod_inicio)
from app.mod_inicio.controllers import mod_inicio as inicio_module

# Registrar blueprint(s)
app.register_blueprint(inicio_module)
