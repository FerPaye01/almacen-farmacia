# routes/producto_routes.py
from flask import Blueprint, jsonify
from db import init_mysql

productos_bp = Blueprint('productos', __name__)
mysql = None  # Se inicializa desde app.py

@productos_bp.route('/productos', methods=['GET'])
def listar_productos():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM productos")
        productos = cur.fetchall()
        return jsonify(productos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
