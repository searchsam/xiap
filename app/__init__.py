# Importar flask y plantillas de operadores
from flask import Flask, render_template

# Importar SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

# Importar modulo/componente usando la su variable (mod_auth)  del blueprint
from app.mod_inicio.controllers import mod_inicio as inicio_module

# Define el objeto de aplicacion WSGI
app = Flask(__name__)

# Configuraciones
app.config.from_object('config')

# Define el objeto de base de datos que se desea importar
# por los modulos y controloadores
db = SQLAlchemy(app)

# Ejemplo de como hacerse cargo de un error HTTP
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


# Registrar blueprint(s)
app.register_blueprint(inicio_module)

# Construlledo la base de datos
# Esto creara una base de datos usando SQLAlchemy
# db.create_all()
