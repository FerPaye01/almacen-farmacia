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
from flask import Flask, render_template, request, redirect, jsonify

from flask import Flask, render_template, request, jsonify, redirect

app = Flask(__name__)

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

@app.route('/menu')
def menu():
    return render_template('index.html')



# Rutas para los módulos
@app.route('/laboratorio')
def laboratorio():
    return render_template('control_temperatura_humedad.html')

@app.route('/farmacia')
def farmacia():
    return render_template('control_stocks.html')

@app.route('/inventarios')
def inventarios():
    return render_template('gestion_stocks.html')

@app.route('/facturacion')
def facturacion():
    return render_template('gestion_estupefacientes.html')

@app.route('/reportes')
def reportes():
    return render_template('devolucion_almacen_especializado.html')

@app.route('/administracion')
def administracion():
    return render_template('almacenamiento_productos.html')

@app.route('/abastecimiento-central')
def abastecimiento_central():
    return render_template('abastecimiento_central.html')

@app.route('/abastecimiento-transferencia-cas')
def abastecimiento_transferencia():
    return render_template('abastecimiento_transferencia_cas.html')

@app.route('/manejo-productos-inmovilizados-vencidos')
def manejo_productos():
    return render_template('manejo_productos_inmovilizados_vencidos.html')
@app.route('/citas')
def citas():
    return render_template('citas.html')

@app.route('/pacientes')
def pacientes():
    return render_template('pacientes.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


if __name__ == '__main__':
    app.run(debug=True)
