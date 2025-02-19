from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Configuración para almacenamiento de imágenes
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Base de datos SQLite
def init_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS placas (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            codigo TEXT UNIQUE,
                            tipo TEXT,
                            marca TEXT,
                            modelo TEXT,
                            cantidad INTEGER,
                            equivalentes TEXT,
                            imagen TEXT
                          )''')
        conn.commit()

init_db()

# Página de inicio (lista de placas)
@app.route('/')
def index():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM placas")
        placas = cursor.fetchall()
    return render_template('index.html', placas=placas)

# Inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == '04032003':
            session['loggedin'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Contraseña incorrecta')
    return render_template('login.html')

# Cerrar sesión
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    return redirect(url_for('login'))

# Agregar placa
@app.route('/add', methods=['GET', 'POST'])
def add_plate():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        codigo = request.form['codigo']
        tipo = request.form['tipo']
        marca = request.form['marca']
        modelo = request.form['modelo']
        cantidad = request.form['cantidad']
        equivalentes = request.form['equivalentes']
        imagen = request.files['imagen']
        imagen_filename = secure_filename(imagen.filename)
        if imagen_filename:
            imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], imagen_filename))
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO placas (codigo, tipo, marca, modelo, cantidad, equivalentes, imagen) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (codigo, tipo, marca, modelo, cantidad, equivalentes, imagen_filename))
            conn.commit()
        return redirect(url_for('index'))
    return render_template('add_plate.html')

# Editar placa
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_plate(id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        if request.method == 'POST':
            codigo = request.form['codigo']
            tipo = request.form['tipo']
            marca = request.form['marca']
            modelo = request.form['modelo']
            cantidad = request.form['cantidad']
            equivalentes = request.form['equivalentes']
            cursor.execute("UPDATE placas SET codigo=?, tipo=?, marca=?, modelo=?, cantidad=?, equivalentes=? WHERE id=?", 
                           (codigo, tipo, marca, modelo, cantidad, equivalentes, id))
            conn.commit()
            return redirect(url_for('index'))
        cursor.execute("SELECT * FROM placas WHERE id=?", (id,))
        placa = cursor.fetchone()
    return render_template('edit_plate.html', placa=placa)

# Eliminar placa
@app.route('/delete/<int:id>', methods=['POST'])
def delete_plate(id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM placas WHERE id=?", (id,))
        conn.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)