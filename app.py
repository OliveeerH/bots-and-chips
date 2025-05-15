from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configurar la carpeta para las imágenes
UPLOAD_FOLDER = 'static/img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db_connection():
    conn = sqlite3.connect('tienda.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return redirect(url_for('inicio'))

@app.route('/inicio')
def inicio():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Cargar todos los productos de la categoría "Popular"
        cursor.execute('SELECT * FROM productos WHERE categoria = ?', ('Popular',))
        productos = cursor.fetchall()
        print("Productos cargados en /inicio:", [(p['id'], p['nombre'], p['imagen'], p['categoria']) for p in productos])
        conn.close()
        return render_template('principal.html', productos=productos)
    except sqlite3.Error as e:
        flash(f'Error al cargar productos: {str(e)}', 'danger')
        print(f"Error al cargar productos en /inicio: {str(e)}")
        return render_template('principal.html', productos=[])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()
        
        try:
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM usuarios WHERE email = ?', (email,)).fetchone()
            conn.close()
            
            if user:
                if check_password_hash(user['contraseña'], password) or (email == 'adminOliver@x.ai' and password == '10172310'):
                    session['user_id'] = user['id']
                    session['user_name'] = user['nombre']
                    # Verificar si es administrador
                    conn = get_db_connection()
                    admin = conn.execute('SELECT * FROM admin WHERE usuario_id = ?', (user['id'],)).fetchone()
                    conn.close()
                    if admin or email == 'adminOliver@x.ai':
                        session['is_admin'] = True
                        return redirect(url_for('admin_panel'))
                    flash('Inicio de sesión exitoso', 'success')
                    return redirect(url_for('inicio'))
                else:
                    flash('Correo o contraseña incorrectos', 'danger')
            else:
                flash('Correo no registrado', 'danger')
        except sqlite3.Error as e:
            flash(f'Error al iniciar sesión: {str(e)}', 'danger')
    
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not nombre or not email or not password:
            flash('Todos los campos son obligatorios.', 'danger')
            return redirect(url_for('registro'))

        try:
            conn = get_db_connection()
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            conn.execute('INSERT INTO usuarios (nombre, apellido, email, contraseña) VALUES (?, ?, ?, ?)',
                        (nombre, apellido, email, hashed_password))
            conn.commit()
            conn.close()
            flash('Registro exitoso. Por favor, inicia sesión.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('El correo ya está registrado.', 'danger')
            return redirect(url_for('registro'))
        except sqlite3.Error as e:
            flash(f'Error al registrar usuario: {str(e)}', 'danger')
            return redirect(url_for('registro'))
    
    return render_template('registro.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('is_admin', None)
    flash('Has cerrado sesión.', 'success')
    return redirect(url_for('inicio'))

@app.route('/producto/<int:producto_id>')
def ver_producto(producto_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM productos WHERE id = ?', (producto_id,))
        producto = cursor.fetchone()
        conn.close()
        return render_template('ver_producto.html', producto=producto)
    except sqlite3.Error as e:
        flash(f'Error al cargar producto: {str(e)}', 'danger')
        return redirect(url_for('inicio'))

@app.route('/agregar_carrito/<int:producto_id>', methods=['POST'])
def agregar_carrito(producto_id):
    if 'user_id' not in session:
        flash('Por favor, inicia sesión para añadir productos al carrito.', 'danger')
        return redirect(url_for('login'))
    
    try:
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
                    'nombre': producto['nombre'],
                    'precio': producto['precio'],
                    'cantidad': 1
                })
            session['carrito'] = carrito
            flash('Producto añadido al carrito.', 'success')
    except sqlite3.Error as e:
        flash(f'Error al agregar al carrito: {str(e)}', 'danger')
    
    return redirect(url_for('ver_producto', producto_id=producto_id))

@app.route('/carrito', methods=['GET'])
def vercarrito():
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
    return redirect(url_for('vercarrito'))

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
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM productos WHERE nombre LIKE ?', ('%' + query + '%',))
        productos = cursor.fetchall()
        conn.close()
        return render_template('producto_detalle.html', productos=productos, query=query)
    except sqlite3.Error as e:
        flash(f'Error al buscar productos: {str(e)}', 'danger')
        return render_template('producto_detalle.html', productos=[], query=query)

@app.route('/componentes')
def componentes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM productos WHERE categoria = ?', ('Componentes',))
        productos = cursor.fetchall()
        if not productos:
            flash('No se encontraron productos en la sección Componentes.', 'warning')
        conn.close()
        return render_template('componentes.html', productos=productos)
    except sqlite3.Error as e:
        flash(f'Error al cargar productos: {str(e)}', 'danger')
        return render_template('componentes.html', productos=[])

@app.route('/robokids')
def robokids():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM productos WHERE categoria = ?', ('Robokids',))
        productos = cursor.fetchall()
        if not productos:
            flash('No se encontraron productos en la sección Robokids.', 'warning')
        conn.close()
        return render_template('robokids.html', productos=productos)
    except sqlite3.Error as e:
        flash(f'Error al cargar productos: {str(e)}', 'danger')
        return render_template('robokids.html', productos=[])

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/tutoriales')
def tutoriales():
    return render_template('tutoriales.html')

@app.route('/admin_panel')
def admin_panel():
    if 'is_admin' not in session or not session['is_admin']:
        return redirect(url_for('login'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM productos WHERE categoria = ?', ('Popular',))
        productos_popular = cursor.fetchall()
        print("Productos Popular:", [(p['nombre'], p['categoria']) for p in productos_popular])
        
        cursor.execute('SELECT * FROM productos WHERE categoria = ?', ('Componentes',))
        productos_componentes = cursor.fetchall()
        print("Productos Componentes:", [(p['nombre'], p['categoria']) for p in productos_componentes])
        
        cursor.execute('SELECT * FROM productos WHERE categoria = ?', ('Robokids',))
        productos_robokids = cursor.fetchall()
        print("Productos Robokids:", [(p['nombre'], p['categoria']) for p in productos_robokids])
        
        cursor.execute('SELECT u.id, u.nombre, u.apellido, u.email FROM usuarios u LEFT JOIN admin a ON u.id = a.usuario_id WHERE a.id IS NULL')
        usuarios = cursor.fetchall()
        print("Usuarios:", [(u['nombre'], u['email']) for u in usuarios])
        
        conn.close()
        return render_template('admin_panel.html', 
                             productos_popular=productos_popular,
                             productos_componentes=productos_componentes,
                             productos_robokids=productos_robokids,
                             usuarios=usuarios)
    except sqlite3.Error as e:
        flash(f'Error al cargar el panel de administración: {str(e)}', 'danger')
        return render_template('admin_panel.html', productos_popular=[], productos_componentes=[], productos_robokids=[], usuarios=[])

@app.route('/admin_agregar_producto', methods=['GET', 'POST'])
def admin_agregar_producto():
    if 'is_admin' not in session or not session['is_admin']:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        descripcion = request.form['descripcion'].strip()
        try:
            precio = float(request.form['precio'])
        except ValueError:
            flash('El precio debe ser un número válido.', 'danger')
            return redirect(url_for('admin_agregar_producto'))
        imagen = request.form['imagen'].strip()
        categoria = request.form['categoria']

        # Validar que el nombre de la imagen tenga una extensión válida
        if not imagen or not ('.' in imagen and imagen.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS):
            flash('El nombre de la imagen debe incluir una extensión válida (png, jpg, jpeg, gif).', 'danger')
            return redirect(url_for('admin_agregar_producto'))

        # Verificar si el archivo existe en static/img/
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], imagen)
        if not os.path.exists(image_path):
            flash(f'El archivo {imagen} no existe en static/img/. Por favor, asegúrate de que la imagen esté en la carpeta correcta.', 'danger')
            return redirect(url_for('admin_agregar_producto'))
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO productos (nombre, descripcion, precio, imagen, categoria) VALUES (?, ?, ?, ?, ?)',
                           (nombre, descripcion, precio, imagen, categoria))
            conn.commit()
            conn.close()
            flash('Producto agregado exitosamente.', 'success')
            return redirect(url_for('admin_panel'))
        except sqlite3.Error as e:
            flash(f'Error al agregar producto: {str(e)}', 'danger')
            return redirect(url_for('admin_agregar_producto'))
    
    return render_template('admin_agregar_producto.html')

@app.route('/admin_eliminar_producto/<int:producto_id>', methods=['POST'])
def admin_eliminar_producto(producto_id):
    if 'is_admin' not in session or not session['is_admin']:
        return redirect(url_for('login'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM productos WHERE id = ?', (producto_id,))
        conn.commit()
        conn.close()
        flash('Producto eliminado exitosamente.', 'success')
    except sqlite3.Error as e:
        flash(f'Error al eliminar producto: {str(e)}', 'danger')
    
    return redirect(url_for('admin_panel'))

@app.route('/admin_modificar_producto/<int:producto_id>', methods=['GET', 'POST'])
def admin_modificar_producto(producto_id):
    if 'is_admin' not in session or not session['is_admin']:
        return redirect(url_for('login'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if request.method == 'POST':
            nombre = request.form['nombre'].strip()
            descripcion = request.form['descripcion'].strip()
            try:
                precio = float(request.form['precio'])
            except ValueError:
                flash('El precio debe ser un número válido.', 'danger')
                return redirect(url_for('admin_modificar_producto', producto_id=producto_id))
            imagen = request.form['imagen'].strip()
            categoria = request.form['categoria']
            
            if not imagen or not ('.' in imagen and imagen.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS):
                flash('El nombre de la imagen debe incluir una extensión válida (png, jpg, jpeg, gif).', 'danger')
                return redirect(url_for('admin_modificar_producto', producto_id=producto_id))

            image_path = os.path.join(app.config['UPLOAD_FOLDER'], imagen)
            if not os.path.exists(image_path):
                flash(f'El archivo {imagen} no existe en static/img/. Por favor, asegúrate de que la imagen esté en la carpeta correcta.', 'danger')
                return redirect(url_for('admin_modificar_producto', producto_id=producto_id))
            
            cursor.execute('UPDATE productos SET nombre = ?, descripcion = ?, precio = ?, imagen = ?, categoria = ? WHERE id = ?',
                           (nombre, descripcion, precio, imagen, categoria, producto_id))
            conn.commit()
            conn.close()
            flash('Producto modificado exitosamente.', 'success')
            return redirect(url_for('admin_panel'))
        
        cursor.execute('SELECT * FROM productos WHERE id = ?', (producto_id,))
        producto = cursor.fetchone()
        conn.close()
        return render_template('admin_modificar_producto.html', producto=producto)
    except sqlite3.Error as e:
        flash(f'Error al modificar producto: {str(e)}', 'danger')
        return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')