# Ejecutar un servidor de prueba.
from app import app
# flask run --host=0.0.0.0
app.run(host='0.0.0.0', port=5000, debug=True)
