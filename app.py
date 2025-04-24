from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

# Ruta principal
@app.route('/')
def index():
    conn = sqlite3.connect('tienda.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    conn.close()
    return render_template('index.html', productos=productos)

if __name__ == '__main__':
    app.run(debug=True)




