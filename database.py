import sqlite3
import os

DB_NAME = "tienda.db"

def init_db():
    if os.path.exists(DB_NAME):
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Crear tabla de usuarios
    cursor.execute('''
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT,
            correo TEXT NOT NULL UNIQUE,
            contraseña TEXT NOT NULL
        )
    ''')

    # Crear tabla de administradores
    cursor.execute('''
        CREATE TABLE admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    ''')

    # Crear tabla de productos
    cursor.execute('''
        CREATE TABLE productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            precio REAL NOT NULL,
            imagen TEXT
        )
    ''')

    # Insertar productos si la tabla está vacía
    productos = [
        ('Carrito Robótico', 'Ideal para aprender robótica básica.', 399, 'carrito-robotico.png'),
        ('Seguidor de líneas', 'Sigue líneas automáticamente.', 449, 'seguidor-lineas.png'),
        ('Robokids Caminador', 'Se mueve en todas direcciones.', 199, 'robokids-caminador.png'),
        ('Tanque Robótico', 'Potente, ideal para exteriores.', 1699, 'tanque-robotico.png')
    ]

    cursor.executemany('INSERT INTO productos (nombre, descripcion, precio, imagen) VALUES (?, ?, ?, ?)', productos)
    conn.commit()
    conn.close()

# Llamada a la función para crear la base de datos e insertar los productos si es necesario
if __name__ == '__main__':
    init_db()


