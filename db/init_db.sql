
CREATE DATABASE IF NOT EXISTS aea_farmacia;
USE aea_farmacia;

CREATE TABLE IF NOT EXISTS usuarios (
  usuario_id   INT AUTO_INCREMENT PRIMARY KEY,
  nombre       VARCHAR(100) NOT NULL,
  correo       VARCHAR(100) UNIQUE NOT NULL,
  clave        VARCHAR(255) NOT NULL,
  rol          VARCHAR(50) DEFAULT 'usuario',
  creado_en    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla maestra de productos y dispositivos
CREATE TABLE IF NOT EXISTS productos (
  producto_id        INT AUTO_INCREMENT PRIMARY KEY,
  codigo_sap         VARCHAR(50) UNIQUE NOT NULL,
  nombre             VARCHAR(200) NOT NULL,
  tipo               VARCHAR(50)  NOT NULL,
  es_controlado      BOOLEAN      DEFAULT FALSE,
  unidad_medida      VARCHAR(20)  NOT NULL,
  created_at         TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
  updated_at         TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Almacenes/Centros de almacenamiento
CREATE TABLE IF NOT EXISTS almacenes (
  almacen_id         INT AUTO_INCREMENT PRIMARY KEY,
  nombre             VARCHAR(100) NOT NULL,
  tipo               VARCHAR(50)  NOT NULL,
  ubicacion          VARCHAR(200),
  created_at         TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- STOCK ACTUAL por producto y almacén
CREATE TABLE IF NOT EXISTS stock (
  stock_id           INT AUTO_INCREMENT PRIMARY KEY,
  producto_id        INT NOT NULL,
  almacen_id         INT NOT NULL,
  cantidad           INT NOT NULL CHECK (cantidad >= 0),
  fecha_actualizacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(producto_id, almacen_id),
  FOREIGN KEY (producto_id) REFERENCES productos(producto_id),
  FOREIGN KEY (almacen_id) REFERENCES almacenes(almacen_id)
);

-- Gestión de Stocks
CREATE TABLE IF NOT EXISTS movimientos_stock (
  movimiento_id      INT AUTO_INCREMENT PRIMARY KEY,
  stock_id           INT NOT NULL,
  tipo_movimiento    VARCHAR(20) NOT NULL,
  cantidad           INT NOT NULL,
  motivo             VARCHAR(200),
  realizado_por      VARCHAR(100),
  fecha              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (stock_id) REFERENCES stock(stock_id)
);

-- Abastecimiento por Almacén Central
CREATE TABLE IF NOT EXISTS abastecimientos_central (
  abastecimiento_id  INT AUTO_INCREMENT PRIMARY KEY,
  producto_id        INT NOT NULL,
  cantidad           INT NOT NULL,
  fecha              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  almacen_destino    INT NOT NULL,
  responsable        VARCHAR(100),
  FOREIGN KEY (producto_id) REFERENCES productos(producto_id),
  FOREIGN KEY (almacen_destino) REFERENCES almacenes(almacen_id)
);

-- Transferencias entre CAS
CREATE TABLE IF NOT EXISTS transferencias (
  transferencia_id   INT AUTO_INCREMENT PRIMARY KEY,
  producto_id        INT NOT NULL,
  cantidad           INT NOT NULL,
  almacen_origen     INT NOT NULL,
  almacen_destino    INT NOT NULL,
  fecha              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  responsable        VARCHAR(100),
  FOREIGN KEY (producto_id) REFERENCES productos(producto_id),
  FOREIGN KEY (almacen_origen) REFERENCES almacenes(almacen_id),
  FOREIGN KEY (almacen_destino) REFERENCES almacenes(almacen_id)
);

-- Almacenamiento
CREATE TABLE IF NOT EXISTS ubicaciones_internas (
  ubicacion_id       INT AUTO_INCREMENT PRIMARY KEY,
  almacen_id         INT NOT NULL,
  codigo             VARCHAR(50) NOT NULL,
  descripcion        VARCHAR(200),
  UNIQUE(almacen_id, codigo),
  FOREIGN KEY (almacen_id) REFERENCES almacenes(almacen_id)
);

CREATE TABLE IF NOT EXISTS stock_ubicacion (
  stock_ubic_id      INT AUTO_INCREMENT PRIMARY KEY,
  stock_id           INT NOT NULL,
  ubicacion_id       INT NOT NULL,
  cantidad           INT NOT NULL CHECK (cantidad >= 0),
  FOREIGN KEY (stock_id) REFERENCES stock(stock_id),
  FOREIGN KEY (ubicacion_id) REFERENCES ubicaciones_internas(ubicacion_id)
);

-- Recepción de estupefacientes y psicotrópicos
CREATE TABLE IF NOT EXISTS recepciones_controlados (
  recepcion_id       INT AUTO_INCREMENT PRIMARY KEY,
  producto_id        INT NOT NULL,
  lote               VARCHAR(100) NOT NULL,
  fecha_vencimiento  DATE NOT NULL,
  cantidad           INT NOT NULL,
  fecha_recepcion    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  recibido_por       VARCHAR(100),
  FOREIGN KEY (producto_id) REFERENCES productos(producto_id)
);

-- Manejo de productos inmovilizados, vencidos y deteriorados
CREATE TABLE IF NOT EXISTS productos_inmovilizados (
  inmovilizado_id    INT AUTO_INCREMENT PRIMARY KEY,
  producto_id        INT NOT NULL,
  almacen_id         INT NOT NULL,
  cantidad           INT NOT NULL,
  fecha_registro     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  motivo             VARCHAR(200),
  FOREIGN KEY (producto_id) REFERENCES productos(producto_id),
  FOREIGN KEY (almacen_id) REFERENCES almacenes(almacen_id)
);

-- Control y registro de temperatura y humedad
CREATE TABLE IF NOT EXISTS log_temp_humedad (
  log_id             INT AUTO_INCREMENT PRIMARY KEY,
  almacen_id         INT NOT NULL,
  temperatura        DECIMAL(5,2),
  humedad            DECIMAL(5,2),
  registrado_por     VARCHAR(100),
  fecha_registro     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (almacen_id) REFERENCES almacenes(almacen_id)
);

-- Devolución al almacén especializado
CREATE TABLE IF NOT EXISTS devoluciones_especializadas (
  devolucion_id      INT AUTO_INCREMENT PRIMARY KEY,
  producto_id        INT NOT NULL,
  cantidad           INT NOT NULL,
  almacen_origen     INT NOT NULL,
  almacen_destino    INT NOT NULL,
  fecha              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  motivo             VARCHAR(200),
  gestionado_por     VARCHAR(100),
  FOREIGN KEY (producto_id) REFERENCES productos(producto_id),
  FOREIGN KEY (almacen_origen) REFERENCES almacenes(almacen_id),
  FOREIGN KEY (almacen_destino) REFERENCES almacenes(almacen_id)
);