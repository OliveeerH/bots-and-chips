from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from db import init_db

app = Flask(__name__)
app.secret_key = 'mi_clave_secreta'

init_db()

def conectar_db():
    try:
        conn = sqlite3.connect('tienda.db')
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

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

@app.route('/buscar', methods=['GET'])
def buscar():
    query = request.args.get('query', '')
    conn = conectar_db()
    if conn is None:
        return "Error: No se pudo conectar a la base de datos.", 500
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos WHERE nombre LIKE ?", ('%' + query + '%',))
        productos = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error al ejecutar la consulta: {e}")
        return "Error: No se pudo buscar productos.", 500
    finally:
        conn.close()
    return render_template('principal.html', productos=productos)

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
        
        # Verificar si el producto ya está en el carrito
        carrito = session['carrito']
        for item in carrito:
            if item['id'] == producto_id:
                item['cantidad'] += 1
                session.modified = True
                conn.close()
                return redirect(url_for('ver_carrito'))

        # Si no está, añadirlo
        carrito.append({
            'id': producto[0],
            'nombre': producto[1],
            'precio': producto[3],
            'cantidad': 1
        })
        session['carrito'] = carrito
        session.modified = True
    except sqlite3.Error as e:
        print(f"Error al ejecutar la consulta: {e}")
        return "Error al agregar al carrito.", 500
    finally:
        conn.close()

    return redirect(url_for('ver_carrito'))

@app.route('/eliminar_del_carrito/<int:producto_id>', methods=['POST'])
def eliminar_del_carrito(producto_id):
    if 'carrito' in session:
        carrito = session['carrito']
        session['carrito'] = [item for item in carrito if item['id'] != producto_id]
        session.modified = True
    return redirect(url_for('ver_carrito'))

@app.route('/carrito', methods=['GET'])
def ver_carrito():
    carrito = session.get('carrito', [])
    total = sum(item['precio'] * item['cantidad'] for item in carrito)
    return render_template('carrito.html', carrito=carrito, total=total)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        contraseña = request.form['contraseña']
        conn = conectar_db()
        if conn is None:
            return "Error: No se pudo conectar a la base de datos.", 500
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT contraseña FROM usuarios WHERE correo = ?", (correo,))
            result = cursor.fetchone()
            if result and check_password_hash(result[0], contraseña):
                return redirect(url_for('index'))
            else:
                return "Correo o contraseña incorrectos.", 401
        except sqlite3.Error as e:
            print(f"Error al verificar usuario: {e}")
            return "Error: No se pudo verificar el usuario.", 500
        finally:
            conn.close()
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        correo = request.form['correo']
        contraseña = generate_password_hash(request.form['contraseña'], method='pbkdf2:sha256')
        conn = conectar_db()
        if conn is None:
            return "Error: No se pudo conectar a la base de datos.", 500
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (nombre, apellido, correo, contraseña) VALUES (?, ?, ?, ?)",
                          (nombre, apellido, correo, contraseña))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Error: El correo ya está registrado.", 400
        except sqlite3.Error as e:
            print(f"Error al registrar usuario: {e}")
            return "Error: No se pudo registrar el usuario.", 500
        finally:
            conn.close()
        return redirect(url_for('index'))
    return render_template('registro.html')

@app.route('/pagar', methods=['POST'])
def pagar():
    session.pop('carrito', None)
    return render_template('pago_completado.html')

@app.route('/inicio')
def inicio():
    return render_template('principal.html')
if __name__ == '__main__':
    app.run(debug=True)