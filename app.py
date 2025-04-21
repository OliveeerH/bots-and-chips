from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta'

# Crear base de datos y tabla si no existe
def init_db():
    conn = sqlite3.connect('tienda.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            precio REAL NOT NULL
        )
    ''')
    # Agregar algunos productos si la tabla está vacía
    cursor.execute('SELECT COUNT(*) FROM productos')
    if cursor.fetchone()[0] == 0:
        productos = [
            ('Carrito Robótico', 'Ideal para aprender robótica básica.', 399),
            ('Seguidor de líneas', 'Sigue líneas automáticamente.', 449),
            ('Robokids Caminador', 'Se mueve en todas direcciones.', 199),
            ('Tanque Robótico', 'Potente, ideal para exteriores.', 1699)
        ]
        cursor.executemany('INSERT INTO productos (nombre, descripcion, precio) VALUES (?, ?, ?)', productos)
    conn.commit()
    conn.close()

# Ruta principal
@app.route('/')
def index():
    conn = sqlite3.connect('tienda.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    conn.close()
    return render_template('index.html', productos=productos)

# Ruta para login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contraseña = request.form['contraseña']
        # Aquí podrías conectar a una base de datos real
        if usuario == 'admin' and contraseña == '1234':
            session['usuario'] = usuario
            return redirect(url_for('index'))
        else:
            return "Credenciales incorrectas"
    return render_template('login.html')

# Ruta para registro (solo vista de ejemplo)
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        # Aquí guardarías el nuevo usuario
        return redirect(url_for('login'))
    return render_template('registro.html')

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('index'))

# Inicializar base de datos solo si el archivo no existe
if not os.path.exists('tienda.db'):
    init_db()

if __name__ == '__main__':
    app.run(debug=True)


