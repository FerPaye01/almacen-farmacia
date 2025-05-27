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

##"LOGIN"


@app.route('/login')
def login_view():
    return render_template('login.html')

@app.route('/menu')
def menu():
    return render_template('index.html')


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

if __name__ == '__main__':
    app.run(debug=True)
