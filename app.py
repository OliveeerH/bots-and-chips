from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from db import init_db  # Importamos init_db desde db.py

app = Flask(__name__)

# Configuración de la clave secreta para manejar sesiones
app.secret_key = 'mi_clave_secreta'

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
    return render_template('principal.html', productos=productos)

# Ruta para ver detalles de un producto
@app.route('/producto/<int:producto_id>')
def ver_producto(producto_id):
    conn = conectar_db()
    if conn is None:
        return "Error: No se pudo conectar a la base de datos.", 500
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos WHERE id = ?", (producto_id,))
        producto = cursor.fetchone()
        if producto is None:
            return "Producto no encontrado", 404
    except sqlite3.Error as e:
        print(f"Error al ejecutar la consulta: {e}")
        return "Error al obtener el producto.", 500
    finally:
        conn.close()
    return render_template('ver_producto.html', producto=producto)

# Ruta para agregar productos al carrito
@app.route('/agregar_carrito/<int:producto_id>', methods=['POST'])
def agregar_carrito(producto_id):
    if 'carrito' not in session:
        session['carrito'] = []

    conn = conectar_db()
    if conn is None:
        return "Error: No se pudo conectar a la base de datos.", 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos WHERE id = ?", (producto_id,))
        producto = cursor.fetchone()
        if producto is None:
            return "Producto no encontrado", 404
        
        # Agregar el producto al carrito (por su ID y cantidad)
        session['carrito'].append({
            'id': producto[0],
            'nombre': producto[1],
            'precio': producto[3],
            'cantidad': 1  # Asumimos que se agrega 1 por defecto
        })
        session.modified = True  # Marcar la sesión como modificada
    except sqlite3.Error as e:
        print(f"Error al ejecutar la consulta: {e}")
        return "Error al agregar al carrito.", 500
    finally:
        conn.close()

    return redirect(url_for('ver_carrito'))

# Ruta para ver el carrito
@app.route('/carrito', methods=['GET'])
def ver_carrito():
    carrito = session.get('carrito', [])
    total = sum(item['precio'] * item['cantidad'] for item in carrito)
    return render_template('carrito.html', carrito=carrito, total=total)

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

# Ruta para pagar (simulación)
@app.route('/pagar', methods=['POST'])
def pagar():
    # Aquí deberías integrar con una API de pago real (por ejemplo, Stripe, PayPal, etc.)
    session.pop('carrito', None)  # Vaciar el carrito después de pagar
    return render_template('pago_completado.html')  # Página de confirmación de pago

if __name__ == '__main__':
    app.run(debug=True)



