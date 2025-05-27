# routes/auth_routes.py
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from db import init_mysql

auth_bp = Blueprint('auth', __name__)
mysql = None  # será inyectado desde app.py

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    correo = data.get('correo')
    clave = data.get('clave')

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE correo = %s", (correo,))
        user = cur.fetchone()

        if user and user['clave'] == clave:  # luego cambiar a check_password_hash
            return jsonify({
                "mensaje": "Login exitoso",
                "usuario": {
                    "id": user['usuario_id'],
                    "nombre": user['nombre'],
                    "correo": user['correo'],
                    "rol": user['rol']
                }
            })
        else:
            return jsonify({"error": "Credenciales inválidas"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500
