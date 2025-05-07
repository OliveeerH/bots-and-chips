import sqlite3
import os

DB_NAME = "tienda.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT,
            correo TEXT NOT NULL UNIQUE,
            contraseña TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            precio REAL NOT NULL,
            imagen TEXT
        )
    ''')

    cursor.execute("SELECT COUNT(*) FROM productos")
    count = cursor.fetchone()[0]

    if count == 0:
        productos = [
            ('Carrito Robótico', 'Ideal para aprender robótica básica.', 399, 'carrito_robotico.png'),
            ('Seguidor de líneas', 'Sigue líneas automáticamente.', 449, 'seguidor_de_linea.png'),
            ('Robokids Caminador', 'Se mueve en todas direcciones.', 199, 'robokids_caminador.png'),
            ('Tanque Robótico', 'Potente, ideal para exteriores.', 1699, 'tanque_robotico.png'),
            ('Kit de Sensores', 'Perfecto para proyectos avanzados.', 299, 'kit_sensores.png')
        ]
        cursor.executemany('INSERT INTO productos (nombre, descripcion, precio, imagen) VALUES (?, ?, ?, ?)', productos)

    conn.commit()
    conn.close()
    print("Base de datos inicializada correctamente.")

if __name__ == '__main__':
    init_db()