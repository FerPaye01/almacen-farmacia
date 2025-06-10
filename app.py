from flask import Flask
from db import init_mysql
from routes.producto_routes import productos_bp
from flask import Blueprint, jsonify
from flask import render_template

app = Flask(__name__)
mysql = init_mysql(app)

from routes.auth_routes import auth_bp
from routes import auth_routes

auth_routes.mysql = mysql
app.register_blueprint(auth_bp)

# Asignar instancia MySQL al blueprint
from routes import producto_routes
producto_routes.mysql = mysql

app.register_blueprint(productos_bp)

from routes.almacenamiento_routes import almacenamiento_bp # ADD THIS LINE

almacenamiento_bp.mysql = mysql # Inject mysql into the new blueprint
app.register_blueprint(almacenamiento_bp) # Register the blueprint

 
@app.route('/')
def home():
    return '🚀 Flask Backend Conectado'

@app.route('/test-db')
def test_db():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT VERSION() AS version")
        result = cur.fetchone()
        return jsonify({"status": "Conectado", "version_mysql": result['version']})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


from flask import Flask, render_template, request, jsonify, redirect

app = Flask(__name__)






@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        correo = data.get('correo')
        clave = data.get('clave')

        if correo == "admin@clinikha.com" and clave == "admin123":
            usuario = {"nombre": "Administrador Clinikha", "correo": correo}
            return jsonify({"usuario": usuario})
        else:
            return jsonify({"error": "Credenciales inválidas"}), 401

    return render_template('login.html')

@app.route('/manejo_productos_inmovilizados_vencidos')
def manejo_productos_inmovilizados_vencidos():
    return render_template('manejo_productos_inmovilizados_vencidos.html')


if __name__ == '__main__':
    app.run(debug=True)
