from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from database import init_db  # Importamos init_db desde database.py

app = Flask(__name__)

# Llamamos a init_db() para asegurarnos de que la base de datos y las tablas existan
init_db()

# Función para conectar a la base de datos
def conectar_db():
    try:
        conn = sqlite3.connect('tienda.db')
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

# Ruta principal
@app.route('/')
def index():
    # Conectar a la base de datos
    conn = conectar_db()
    if conn is None:
        return "Error: No se pudo conectar a la base de datos.", 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos")
        productos = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error al ejecutar la consulta: {e}")
        return "Error: No se pudo obtener los productos.", 500
    finally:
        conn.close()

    return render_template('index.html', productos=productos)

# Ruta para iniciar sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        contraseña = request.form['contraseña']
        # Aquí deberías verificar las credenciales en la base de datos
        # Por ahora, solo redirigimos al index
        return redirect(url_for('index'))
    return render_template('login.html')

# Ruta para registrarse
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        correo = request.form['correo']
        contraseña = request.form['contraseña']
        # Aquí deberías insertar el usuario en la base de datos
        conn = conectar_db()
        if conn is None:
            return "Error: No se pudo conectar a la base de datos.", 500
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (nombre, apellido, correo, contraseña) VALUES (?, ?, ?, ?)",
                          (nombre, apellido, correo, contraseña))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error al registrar usuario: {e}")
            return "Error: No se pudo registrar el usuario.", 500
        finally:
            conn.close()
        return redirect(url_for('index'))
    return render_template('registro.html')

if __name__ == '__main__':
    app.run(debug=True)