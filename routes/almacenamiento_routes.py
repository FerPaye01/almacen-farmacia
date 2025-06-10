# routes/almacenamiento_routes.py
from flask import Blueprint, request, jsonify, render_template
from datetime import datetime

almacenamiento_bp = Blueprint('almacenamiento_bp', __name__)
mysql = None 


@almacenamiento_bp.route('/abastecimiento_central')
def abastecimiento_central():
    return render_template('abastecimiento_central.html')

@almacenamiento_bp.route('/abastecimiento_transferencia_cas')
def abastecimiento_transferencia_cas():
    return render_template('abastecimiento_transferencia_cas.html')

@almacenamiento_bp.route('/almacenamiento_productos')
def almacenamiento_productos():
    return render_template('almacenamiento_productos.html')

@almacenamiento_bp.route('/control_stocks')
def control_stocks():
    return render_template('control_stocks.html')

@almacenamiento_bp.route('/control_temperatura_humedad')
def control_temperatura_humedad():
    return render_template('control_temperatura_humedad.html')

@almacenamiento_bp.route('/devolucion_almacen_especializado')
def devolucion_almacen_especializado():
    return render_template('devolucion_almacen_especializado.html')

@almacenamiento_bp.route('/gestion_estupefacientes')
def gestion_estupefacientes():
    return render_template('gestion_estupefacientes.html')

@almacenamiento_bp.route('/gestion_stocks')
def gestion_stocks():
    return render_template('gestion_stocks.html')

@almacenamiento_bp.route('/manejo_productos_inmovilizados_vencidos')
def manejo_productos_inmovilizados_vencidos():
    return render_template('manejo_productos_inmovilizados_vencidos.html')




@almacenamiento_bp.route('/almacenamiento_productos')
def almacenamiento_productos_page():
    # Esta ruta renderiza la página HTML
    return render_template('almacenamiento_productos.html')

# API para obtener ubicaciones
@almacenamiento_bp.route('/api/locations', methods=['GET'])
def get_locations():
    if mysql is None:
        return jsonify({"error": "Conexión a base de datos no inicializada"}), 500

    cur = mysql.connection.cursor()
    try:
        query = """
            SELECT
                ui.ubicacion_id AS id,
                ui.codigo AS name,
                ui.descripcion,
                # Subconsulta para obtener la suma de cantidad de productos en esta ubicación
                COALESCE(SUM(su.cantidad), 0) AS current_items,
                # Capacidad de la ubicación - ASUMIMOS UN VALOR FIJO POR AHORA, AJUSTA TU ESQUEMA DE BD
                100 AS capacity # <--- REEMPLAZA ESTO CON UNA COLUMNA REAL DE CAPACIDAD EN 'ubicaciones_internas'
            FROM
                ubicaciones_internas ui
            LEFT JOIN
                stock_ubicacion su ON ui.ubicacion_id = su.ubicacion_id
            GROUP BY
                ui.ubicacion_id, ui.codigo, ui.descripcion
        """
        cur.execute(query)
        locations_data = cur.fetchall()

        # Flask-MySQLdb con DictCursor ya devuelve diccionarios, no necesitamos post-procesar

        return jsonify(locations_data)
    except Exception as e:
        print(f"Error al obtener ubicaciones: {e}")
        return jsonify({"error": f"Error interno del servidor al obtener ubicaciones: {str(e)}"}), 500
    finally:
        cur.close()

# API para obtener la paleta de productos
@almacenamiento_bp.route('/api/products_palette', methods=['GET'])
def get_products_palette():
    if mysql is None:
        return jsonify({"error": "Conexión a base de datos no inicializada"}), 500

    cur = mysql.connection.cursor()
    try:
        query = "SELECT producto_id AS id, nombre, codigo_sap FROM productos"
        cur.execute(query)
        products_data = cur.fetchall()
        return jsonify(products_data)
    except Exception as e:
        print(f"Error al obtener paleta de productos: {e}")
        return jsonify({"error": f"Error interno del servidor al obtener productos: {str(e)}"}), 500
    finally:
        cur.close()

# API para asignar un producto a una ubicación (Drag & Drop)
@almacenamiento_bp.route('/api/assign-product', methods=['POST'])
def assign_product():
    data = request.get_json()
    product_id = data.get('product_id')
    location_id = data.get('location_id')
    quantity = 1 # Asignaremos 1 unidad por cada drag-drop simple

    if not product_id or not location_id:
        return jsonify({"error": "Datos incompletos: product_id y location_id son requeridos"}), 400

    cur = mysql.connection.cursor()
    try:
        # Obtener el `almacen_id` de la `ubicacion_id`
        cur.execute("SELECT almacen_id FROM ubicaciones_internas WHERE ubicacion_id = %s", (location_id,))
        almacen_record = cur.fetchone()
        if not almacen_record:
            return jsonify({"error": "Ubicación interna no encontrada para determinar el almacén"}), 404
        almacen_id = almacen_record['almacen_id'] # Si DictCursor está activo

        # 1. Gestionar `stock` (total por producto en el almacén)
        cur.execute("SELECT stock_id, cantidad FROM stock WHERE producto_id = %s AND almacen_id = %s",
                       (product_id, almacen_id))
        stock_record = cur.fetchone()

        stock_id = None
        if stock_record:
            stock_id = stock_record['stock_id']
            new_stock_quantity = stock_record['cantidad'] + quantity
            cur.execute("UPDATE stock SET cantidad = %s, fecha_actualizacion = NOW() WHERE stock_id = %s",
                           (new_stock_quantity, stock_id))
        else:
            cur.execute("INSERT INTO stock (producto_id, almacen_id, cantidad) VALUES (%s, %s, %s)",
                           (product_id, almacen_id, quantity))
            stock_id = cur.lastrowid # Obtener el ID del nuevo registro de stock

        # 2. Gestionar `stock_ubicacion` (por producto en la ubicación específica)
        cur.execute("SELECT stock_ubic_id, cantidad FROM stock_ubicacion WHERE stock_id = %s AND ubicacion_id = %s",
                       (stock_id, location_id))
        stock_ubic_record = cur.fetchone()

        if stock_ubic_record:
            new_ubic_quantity = stock_ubic_record['cantidad'] + quantity
            cur.execute("UPDATE stock_ubicacion SET cantidad = %s WHERE stock_ubic_id = %s",
                           (new_ubic_quantity, stock_ubic_record['stock_ubic_id']))
        else:
            cur.execute("INSERT INTO stock_ubicacion (stock_id, ubicacion_id, cantidad) VALUES (%s, %s, %s)",
                           (stock_id, location_id, quantity))
        
        mysql.connection.commit()
        return jsonify({"message": f"Producto asignado a ubicación {location_id}."})

    except Exception as e:
        mysql.connection.rollback()
        print(f"Error al asignar producto: {e}")
        return jsonify({"error": f"Error interno del servidor al asignar producto: {str(e)}"}), 500
    finally:
        cur.close()

# API para obtener detalles de una ubicación específica
@almacenamiento_bp.route('/api/location_details/<int:location_id>', methods=['GET'])
def get_location_details(location_id):
    if mysql is None:
        return jsonify({"error": "Conexión a base de datos no inicializada"}), 500

    cur = mysql.connection.cursor()
    try:
        # Obtener información básica de la ubicación
        cur.execute("SELECT ubicacion_id AS id, codigo AS name, descripcion FROM ubicaciones_internas WHERE ubicacion_id = %s", (location_id,))
        location_data = cur.fetchone()
        if not location_data:
            return jsonify({"error": "Ubicación no encontrada"}), 404

        # Obtener productos específicos en esa ubicación
        query_products = """
            SELECT
                p.nombre AS name,
                su.cantidad,
                'N/A' AS batch, -- Lote no está directamente en stock_ubicacion, necesita ser gestionado
                'N/A' AS expiration_date -- Vencimiento no está directamente en stock_ubicacion
            FROM
                stock_ubicacion su
            JOIN
                stock s ON su.stock_id = s.stock_id
            JOIN
                productos p ON s.producto_id = p.producto_id
            WHERE
                su.ubicacion_id = %s
        """
        cur.execute(query_products, (location_id,))
        products_in_location = cur.fetchall()

        # Calcular items actuales y capacidad (asume una capacidad fija, como antes)
        total_items = sum(p['cantidad'] for p in products_in_location)
        location_data['current_items'] = total_items
        location_data['capacity'] = 100 # <--- REEMPLAZA ESTO CON UNA COLUMNA REAL DE CAPACIDAD EN 'ubicaciones_internas'
        location_data['products'] = products_in_location

        return jsonify(location_data)
    except Exception as e:
        print(f"Error al obtener detalles de ubicación: {e}")
        return jsonify({"error": f"Error interno del servidor al obtener detalles de ubicación: {str(e)}"}), 500
    finally:
        cur.close()

# API para registrar condiciones (temperatura y humedad)
@almacenamiento_bp.route('/api/record-conditions', methods=['POST'])
def record_conditions():
    data = request.get_json()
    ubicacion_codigo = data.get('ubicacion') # Código de la ubicación, ej: "A1-01"
    temperatura = data.get('temperatura')
    humedad = data.get('humedad')
    # Idealmente, 'registrado_por' vendría del usuario autenticado en la sesión
    registrado_por = "Usuario_Sistema" # Placeholder por ahora

    if not ubicacion_codigo or temperatura is None or humedad is None:
        return jsonify({"error": "Datos incompletos para registrar condiciones"}), 400

    cur = mysql.connection.cursor()
    try:
        # Obtener el almacen_id de la ubicacion_interna
        cur.execute("SELECT almacen_id FROM ubicaciones_internas WHERE codigo = %s LIMIT 1", (ubicacion_codigo,))
        almacen_record = cur.fetchone()
        
        if not almacen_record:
            return jsonify({"error": "Código de ubicación no válido o no encontrado"}), 404
        
        almacen_id = almacen_record['almacen_id']

        query = """
            INSERT INTO log_temp_humedad (almacen_id, temperatura, humedad, registrado_por, fecha_registro)
            VALUES (%s, %s, %s, %s, NOW())
        """
        cur.execute(query, (almacen_id, temperatura, humedad, registrado_por))
        mysql.connection.commit()
        return jsonify({"message": "Condiciones registradas correctamente."})
    except Exception as e:
        mysql.connection.rollback()
        print(f"Error al registrar condiciones: {e}")
        return jsonify({"error": f"Error interno del servidor al registrar condiciones: {str(e)}"}), 500
    finally:
        cur.close()