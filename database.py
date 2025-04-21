import sqlite3
import os

DB_NAME = "tienda.db"

def init_db():
    if os.path.exists(DB_NAME):
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Tabla de usuarios
    cursor.execute('''
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT,
            correo TEXT NOT NULL UNIQUE,
            contraseña TEXT NOT NULL
        )
    ''')

    # Tabla de administradores
    cursor.execute('''
        CREATE TABLE admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    ''')

    # Tabla de productos
    cursor.execute('''
        CREATE TABLE productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            precio REAL NOT NULL,
            imagen TEXT
        )
    ''')

    conn.commit()
    conn.close()

