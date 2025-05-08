from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('tienda.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return redirect(url_for('inicio'))

@app.route('/inicio')
def inicio():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM productos')
    productos = cursor.fetchall()
    conn.close()
    return render_template('principal.html', productos=productos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM usuarios WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['contraseña'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['nombre']
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('inicio'))
        else:
            flash('Correo o contraseña incorrectos', 'danger')
    
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        # Validación básica
        if not nombre or not email or not password:
            flash('Todos los campos son obligatorios.', 'danger')
            return redirect(url_for('registro'))

        conn = get_db_connection()
        try:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            conn.execute('INSERT INTO usuarios (nombre, apellido, email, contraseña) VALUES (?, ?, ?, ?)',
                        (nombre, apellido, email, hashed_password))
            conn.commit()
            flash('Registro exitoso. Por favor, inicia sesión.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('El correo ya está registrado.', 'danger')
            return redirect(url_for('registro'))
        except sqlite3.Error as e:
            flash(f'Error al registrar usuario: {e}', 'danger')
            return redirect(url_for('registro'))
        finally:
            conn.close()
    
    return render_template('registro.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    flash('Has cerrado sesión.', 'success')
    return redirect(url_for('inicio'))

@app.route('/producto/<int:producto_id>')
def ver_producto(producto_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM productos WHERE id = ?', (producto_id,))
    producto = cursor.fetchone()
    conn.close()
    return render_template('ver_producto.html', producto=producto)

@app.route('/agregar_carrito/<int:producto_id>', methods=['POST'])
def agregar_carrito(producto_id):
    if 'user_id' not in session:
        flash('Por favor, inicia sesión para añadir productos al carrito.', 'danger')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM productos WHERE id = ?', (producto_id,))
    producto = cursor.fetchone()
    conn.close()
    
    if producto:
        carrito = session.get('carrito', [])
        for item in carrito:
            if item['id'] == producto_id:
                item['cantidad'] += 1
                break
        else:
            carrito.append({
                'id': producto_id,
                'nombre': producto[1],
                'precio': producto[3],
                'cantidad': 1
            })
        session['carrito'] = carrito
        flash('Producto añadido al carrito.', 'success')
    
    return redirect(url_for('ver_producto', producto_id=producto_id))

@app.route('/carrito', methods=['GET'])
def ver_carrito():
    if 'user_id' not in session:
        flash('Por favor, inicia sesión para ver el carrito.', 'danger')
        return redirect(url_for('login'))
    
    carrito = session.get('carrito', [])
    total = sum(item['precio'] * item['cantidad'] for item in carrito)
    return render_template('carrito.html', carrito=carrito, total=total)

@app.route('/eliminar_del_carrito/<int:producto_id>', methods=['POST'])
def eliminar_del_carrito(producto_id):
    if 'user_id' not in session:
        flash('Por favor, inicia sesión para modificar el carrito.', 'danger')
        return redirect(url_for('login'))
    
    carrito = session.get('carrito', [])
    carrito = [item for item in carrito if item['id'] != producto_id]
    session['carrito'] = carrito
    flash('Producto eliminado del carrito.', 'success')
    return redirect(url_for('ver_carrito'))

@app.route('/pagar', methods=['POST'])
def pagar():
    if 'user_id' not in session:
        flash('Por favor, inicia sesión para realizar el pago.', 'danger')
        return redirect(url_for('login'))
    
    session['carrito'] = []
    flash('Compra realizada con éxito.', 'success')
    return redirect(url_for('pago_completado'))

@app.route('/pago_completado')
def pago_completado():
    return render_template('pago_completado.html')

@app.route('/buscar', methods=['GET'])
def buscar():
    query = request.args.get('q', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM productos WHERE nombre LIKE ?', ('%' + query + '%',))
    productos = cursor.fetchall()
    conn.close()
    return render_template('producto_detalle.html', productos=productos, query=query)

@app.route('/componentes')
def componentes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM productos')
    productos = cursor.fetchall()
    conn.close()
    return render_template('componentes.html', productos=productos)

@app.route('/robokids')
def robokids():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM productos')
    productos = cursor.fetchall()
    conn.close()
    return render_template('robokids.html', productos=productos)

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/tutoriales')
def tutoriales():
    return render_template('tutoriales.html')

if __name__ == '__main__':
    app.run(debug=True)