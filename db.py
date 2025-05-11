import sqlite3
import os

DB_NAME = "tienda.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Crear tablas si no existen
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT,
            email TEXT NOT NULL UNIQUE,
            contraseña TEXT NOT NULL,
            google_id TEXT,
            facebook_id TEXT,
            twitter_id TEXT
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

    # Verificar si las tablas están vacías antes de insertar datos iniciales
    cursor.execute('SELECT COUNT(*) FROM productos')
    if cursor.fetchone()[0] == 0:
        productos = [
            ('Carrito Robótico', 'Ideal para aprender robótica básica.', 399, 'carrito_robotico.png'),
            ('Seguidor de líneas', 'Sigue líneas automáticamente.', 449, 'seguidor_de_linea.png'),
            ('Robokids Caminador', 'Se mueve en todas direcciones.', 199, 'robokids-caminador.png'),
            ('Tanque Robótico', 'Potente, ideal para exteriores.', 1699, 'tanque_robotico.png'),
            ('Kit de Sensores', 'Perfecto para proyectos avanzados.', 299, 'kit_sensores.png'),
            ('Arduino Uno', 'Placa de desarrollo para proyectos electrónicos.', 399.00, 'arduino'),
            ('10 Moto Reductores', 'Motores con reductores para robots.', 189.00, 'moto_10'),
            ('Protoboard', 'Placa para prototipos electrónicos.', 69.00, 'proto'),
            ('10 Servomotores', 'Servomotores para control preciso.', 259.00, 'servos_10'),
            ('Robokids Insecto', 'Robot insecto para aprendizaje infantil.', 199.00, 'insecto'),
            ('Robokids Panda', 'Robot panda interactivo para niños.', 799.00, 'panda'),
            ('Robot Pintor', 'Robot que pinta con control básico.', 199.00, 'pintor')
        ]

        cursor.executemany('''
            INSERT INTO productos (nombre, descripcion, precio, imagen)
            VALUES (?, ?, ?, ?)
        ''', productos)

    # Inicializar usuario adminOliver solo si no existe
    cursor.execute('SELECT id FROM usuarios WHERE email = ?', ('adminOliver@x.ai',))
    admin_user = cursor.fetchone()
    if not admin_user:
        cursor.execute('''
            INSERT INTO usuarios (nombre, email, contraseña)
            VALUES (?, ?, ?)
        ''', ('Oliver', 'adminOliver@x.ai', '10172310'))
        admin_user_id = cursor.lastrowid
        cursor.execute('INSERT INTO admin (usuario_id) VALUES (?)', (admin_user_id,))
        conn.commit()
    else:
        admin_user_id = admin_user[0]
        cursor.execute('INSERT OR IGNORE INTO admin (usuario_id) VALUES (?)', (admin_user_id,))

    conn.commit()
    conn.close()
    print("Base de datos inicializada o verificada correctamente.")

if __name__ == '__main__':
    init_db()