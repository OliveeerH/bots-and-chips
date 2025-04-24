import sqlite3
import os

DB_NAME = "tienda.db"

def init_db():
    # Conectar a la base de datos (se creará si no existe)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Crear tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT,
            correo TEXT NOT NULL UNIQUE,
            contraseña TEXT NOT NULL
        )
    ''')

    # Crear tabla de administradores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    ''')

    # Crear tabla de productos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            precio REAL NOT NULL,
            imagen TEXT
        )
    ''')

    # Verificar si la tabla productos está vacía
    cursor.execute("SELECT COUNT(*) FROM productos")
    count = cursor.fetchone()[0]

    # Insertar productos solo si la tabla está vacía
    if count == 0:
        productos = [
            ('Carrito Robótico', 'Ideal para aprender robótica básica.', 399, 'carrito-robotico.png'),
            ('Seguidor de líneas', 'Sigue líneas automáticamente.', 449, 'seguidor-lineas.png'),
            ('Robokids Caminador', 'Se mueve en todas direcciones.', 199, 'robokids-caminador.png'),
            ('Tanque Robótico', 'Potente, ideal para exteriores.', 1699, 'tanque-robotico.png')
        ]
        cursor.executemany('INSERT INTO productos (nombre, descripcion, precio, imagen) VALUES (?, ?, ?, ?)', productos)

    # Guardar los cambios y cerrar la conexión
    conn.commit()
    conn.close()
    print("Base de datos inicializada correctamente.")

# Llamada a la función para crear la base de datos e insertar los productos si es necesario
if __name__ == '__main__':
    init_db()