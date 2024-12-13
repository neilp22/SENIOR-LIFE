from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

app = Flask(__name__)
app.secret_key = 'seniorlife_secret_key'

# Inicializar baxse de datos
def init_db():
    conn = sqlite3.connect('database/data.sqlite')
    cursor = conn.cursor()

    # Tabla general de usuarios
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT, -- paciente, familiar, profesional
        nombre TEXT,
        apellidos TEXT,
        email TEXT UNIQUE,
        password TEXT,
        dni TEXT UNIQUE,
        telefono TEXT,
        direccion TEXT,
        sexo TEXT,
        fecha_nacimiento TEXT,
        foto_perfil TEXT
    )''')

    # Tabla específica para pacientes
    cursor.execute('''CREATE TABLE IF NOT EXISTS pacientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        necesita_cadira BOOLEAN,
        contactos_emergencia TEXT,
        historial_medico TEXT,
        wearable TEXT,
        medicacion TEXT,
        videollamada TEXT,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )''')

    # Tabla específica para familiares
    cursor.execute('''CREATE TABLE IF NOT EXISTS familiares (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        paciente_dni TEXT,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )''')

    # Tabla específica para profesionales sanitarios
    cursor.execute('''CREATE TABLE IF NOT EXISTS profesionales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        especialidad TEXT,
        paciente_dni TEXT,
        hospital TEXT,
        num_colegiado TEXT,
        asistencia_domicilio BOOLEAN,
        rol TEXT,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )''')

    conn.commit()
    conn.close()

init_db()

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('database/data.sqlite')
        cursor = conn.cursor()

        # Recuperar usuario basado en email
        cursor.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()

        # Verificar usuario y contraseña
        if user and check_password_hash(user[5], password):  # user[5] es la columna de contraseña
            session['user_id'] = user[0]
            session['user_name'] = f"{user[2]} {user[3]}"  # user[2]: nombre, user[3]: apellidos
            session['user_type'] = user[1]
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Correo o contraseña incorrectos.', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Por favor, inicia sesión primero.', 'error')
        return redirect(url_for('login'))
    
    # Recuperar los datos del usuario desde la base de datos
    user_id = session['user_id']
    conn = sqlite3.connect('database/data.sqlite')
    cursor = conn.cursor()

    # Obtener los datos del usuario por su 'user_id'
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
    user_data = cursor.fetchone()

    # Cerrar la conexión

    user_type = user_data[1]  # Columna 'tipo' en usuarios (índice 1)

    if user_type == 'profesional':
        # Obtener datos del profesional para identificar el rol
        cursor.execute("SELECT rol FROM profesionales WHERE usuario_id = ?", (user_id,))
        professional_data = cursor.fetchone()

        if not professional_data:
            flash('No se encontraron datos específicos del profesional.', 'error')
            return redirect(url_for('login'))

        professional_role = professional_data[0]  # Columna 'rol' (índice 0)

        # Redirigir según el rol del profesional
        if professional_role == 'metge':
            return render_template('dash_doct.html', user_data=user_data)
        elif professional_role == 'infermer':
            return render_template('perfil_enfermero.html', user_data=user_data)
        else:
            flash('Rol profesional desconocido.', 'error')
            return redirect(url_for('login'))
    
    elif user_type == 'familiar':
        return render_template('dash_fam.html',user_data=user_data)
    elif user_type == 'paciente':
        return render_template('dashboard.html',user_data=user_data)
    else:
        flash('Error al determinar el tipo de usuario.', 'error')
        return redirect(url_for('login'))
    
 

# Ruta de registro
@app.route('/register_user', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_type = request.form.get('user-type')

        # Procesar formulario basado en el tipo de usuario
        if user_type == 'pacient':
            save_patient(request.form)
        elif user_type == 'familiar':
            save_family(request.form)
        elif user_type == 'professional':
            save_professional(request.form)

        flash('Registro completado con éxito', 'success')  # Mensaje de éxito
        return redirect(url_for('index'))  # Redirigir al índice después de completar el registro
    return render_template('register_user.html')



def save_patient(form_data):
    conn = sqlite3.connect('database/data.sqlite')
    cursor = conn.cursor()

    # Generar hash de la contraseña
    hashed_password = generate_password_hash(form_data['pacient-password'], method='pbkdf2:sha256', salt_length=16)

    # Insertar datos generales del usuario
    cursor.execute('INSERT INTO usuarios (tipo, nombre, apellidos, email, password, dni, telefono, direccion, sexo, fecha_nacimiento, foto_perfil) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                   ('paciente', form_data['pacient-nom'], form_data['pacient-cognoms'], form_data['pacient-email'], 
                    hashed_password, form_data['pacient-dni'], form_data['pacient-telefon'], 
                    form_data['pacient-direccio'], form_data['pacient-sexe'], form_data['pacient-naixement'], 
                    form_data.get('pacient-foto')))
    usuario_id = cursor.lastrowid

    # Insertar datos específicos del paciente
    cursor.execute('INSERT INTO pacientes (usuario_id, necesita_cadira, contactos_emergencia, historial_medico, wearable, medicacion, videollamada) VALUES (?, ?, ?, ?, ?, ?, ?)',
                   (usuario_id, form_data['pacient-cadira'] == 'si', form_data['pacient-contactes'], form_data['pacient-historial'], 
                    form_data['pacient-wearable'], form_data['pacient-medicaments'], form_data['pacient-videotrucada']))
    conn.commit()
    conn.close()

def save_family(form_data):
    conn = sqlite3.connect('database/data.sqlite')
    cursor = conn.cursor()

    # Generar hash de la contraseña
    hashed_password = generate_password_hash(form_data['familiar-password'], method='pbkdf2:sha256', salt_length=16)

    # Insertar datos generales del usuario
    cursor.execute('INSERT INTO usuarios (tipo, nombre, apellidos, email, password, dni, telefono, direccion, sexo, fecha_nacimiento, foto_perfil) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                   ('familiar', form_data['familiar-nom'], form_data['familiar-cognoms'], form_data['familiar-email'], 
                    hashed_password, form_data['familiar-dni'], form_data['familiar-telefon'], 
                    form_data['familiar-direccio'], form_data['familiar-sexe'], form_data['familiar-naixement'], 
                    form_data.get('familiar-foto')))
    usuario_id = cursor.lastrowid

    # Insertar datos específicos del familiar
    cursor.execute('INSERT INTO familiares (usuario_id, paciente_dni) VALUES (?, ?)',
                   (usuario_id, form_data['familiar-pacient']))
    conn.commit()
    conn.close()

def save_professional(form_data):
    conn = sqlite3.connect('database/data.sqlite')
    cursor = conn.cursor()

    # Generar hash de la contraseña
    hashed_password = generate_password_hash(form_data['professional-password'], method='pbkdf2:sha256', salt_length=16)

    # Insertar datos generales del usuario
    cursor.execute('INSERT INTO usuarios (tipo, nombre, apellidos, email, password, dni, telefono, direccion, sexo, fecha_nacimiento, foto_perfil) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                   ('profesional', form_data['professional-nom'], form_data['professional-cognoms'], form_data['professional-email'], 
                    hashed_password, form_data['professional-dni'], form_data['professional-telefon'], 
                    form_data['professional-direccio'], form_data['professional-sexe'], form_data['professional-naixement'], 
                    form_data.get('professional-foto')))
    usuario_id = cursor.lastrowid

    # Insertar datos específicos del profesional
    cursor.execute('INSERT INTO profesionales (usuario_id, especialidad, paciente_dni, hospital, num_colegiado, asistencia_domicilio, rol) VALUES (?, ?, ?, ?, ?, ?, ?)',
                   (usuario_id, form_data['professional-especialitat'], form_data['professional-pacient'], 
                    form_data['professional-hospital'], form_data['professional-numcol'], 
                    form_data['professional-assistencia'] == 'si', form_data['professional-rol']))
    conn.commit()
    conn.close()

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('index.html'))

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({"error": "No estás autenticado"}), 401

    user_id = session['user_id']
    data = request.json  # Recibir datos en formato JSON

    # Abrir conexión con la base de datos
    conn = sqlite3.connect('database/data.sqlite')
    cursor = conn.cursor()

    # Actualizar la información del usuario
    cursor.execute('''
        UPDATE usuarios
        SET nombre = ?, apellidos = ?, telefono = ?, direccion = ?, sexo = ?, fecha_nacimiento = ?
        WHERE id = ?
    ''', (data['name'], data['surname'], data['phone'], data['address'], data['sex'], data['dob'], user_id))

    conn.commit()
    conn.close()

    return jsonify({"success": "Perfil actualizado correctamente"})


# Ruta para crear una videoconferencia
@app.route('/create-conference', methods=['POST'])
def create_conference():
    user_name = request.json.get('userName', 'Usuario SeniorLife')  # Nombre del usuario enviado desde el frontend

    # Generar un nombre único para la sala
    room_name = f"SeniorLife_{uuid.uuid4().hex[:8]}"

    # Devolver el nombre de la sala y el nombre del usuario
    return jsonify({
        "roomName": room_name,
        "userName": user_name
    })

@app.route('/doctor')
def doctor():
    return render_template('dash_doct.html')

@app.route('/infermera')
def infermera():
    return render_template('perfil_enfermero.html')

@app.route('/alerta')
def alerta():
    return render_template('alerta.html')

@app.route('/chats_doctor')
def chats_doctor():
    return render_template('doctor_chats.html')

@app.route('/config')
def config():
    return render_template('configuracion.html')

@app.route('/privacy')
def priv():
    return render_template('privacy.html')

@app.route('/historial_alerta')
def hist_alerta():
    return render_template('historial_alerta.html')

@app.route('/alerta2')
def alerta2():
    return render_template('alerta2.html')

@app.route('/iot')
def iotenvivo():
    return render_template('iot.html')

@app.route('/iot2')
def iotenvivo2():
    return render_template('iot2.html')

@app.route('/perfil_medico')
def perfil_medico():
    return render_template('perfil_medico.html')

@app.route('/perfil_medico2')
def perfil_medico2():
    return render_template('perfil_medico2.html')

@app.route('/videocall')
def videocall():
    return render_template('video.html')

@app.route('/video_ref')
def video_ref():
    return render_template('video_ref.html')

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/acercade')
def acercade():
    return render_template('acercade.html')

@app.route('/carac')
def carac():
    return render_template('carac.html')

@app.route('/fam')
def fam():
    return render_template('dash_fam.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)




