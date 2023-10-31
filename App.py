from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'  
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'seminario'
mysql = MySQL(app)



@app.route('/')
def Login():
    
    #return redirect(url_for('Inicio'))
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def Autenticar():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT Id_usuario, password FROM registro WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        print("Usuario de la base de datos:", user) 
        if user:
            if check_password_hash(user[1], password):
                session['Id_usuario'] = user[0]
                print("Usuario autenticado correctamente.")  
                return redirect(url_for('Inicio'))
            else:
                flash('Credenciales incorrectas. Por favor, inténtelo de nuevo.')
                print("Contraseña incorrecta.")  
        else:
            flash('Usuario no encontrado. Regístrese para crear una cuenta.')
            print("Usuario no encontrado.")  
    return render_template('login.html')


@app.route('/inicio', methods=['GET'])
def Inicio():
    if 'Id_usuario' in session:
        return render_template('index.html')
    return redirect(url_for('Login'))



@app.route('/registro', methods=['GET', 'POST'])
def Registro():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO registro (email, password) VALUES (%s, %s)', (email, hashed_password))
        mysql.connection.commit()
        flash('Usuario registrado con éxito. Ahora puedes iniciar sesión.')
        return redirect(url_for('Login'))
    return render_template('registro.html')



@app.route('/modificar_usuario', methods=['POST'])
def modificar_usuario():
    if 'Id_usuario' in session:
        Id_usuario = session['Id_usuario']
        Usuario = request.form['Usuario']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        
        cur = mysql.connection.cursor()
        cur.execute('UPDATE registro SET Usuarios = %s, password = %s WHERE Id_usuario = %s', (Usuario, hashed_password, Id_usuario))
        mysql.connection.commit()
        cur.close()
        
        flash('Usuario modificado con éxito')
        return redirect(url_for('Inicio'))
    return redirect(url_for('Login'))


def obtener_Nombre_usuario():
    if 'Id_usuario' in session:
        Id_usuario = session['Id_usuario']
        try:
            conn = mysql.connection
            cursor = conn.cursor()
            cursor.execute('SELECT Usuarios FROM registro WHERE Id_usuario = %s', (Id_usuario,))
            user_name = cursor.fetchone()[0]
            cursor.close()
            return user_name
        except Exception as e:
            print(f"Error al obtener el nombre del usuario: {str(e)}")
    return None

@app.route('/ingresos', methods=['GET'])
def Ingresos():
    if 'Id_usuario' in session:
        user_id = session['Id_usuario']
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_usuario, motivo, monto, fecha FROM ingresos WHERE id_usuario = %s", (user_id,))
        data = cur.fetchall()
        cur.close()
        return render_template('Ingresos.html', data=data)
    return redirect(url_for('Login'))

@app.route('/registroIngreso', methods=['POST'])
def registroIngreso():
    if 'Id_usuario' in session and request.method == 'POST':
        motivo = request.form['motivo']
        monto = request.form['monto']
        fecha = request.form['fecha']
        user_id = session['Id_usuario']

        # Asegúrate de validar y limpiar los datos antes de insertarlos en la base de datos
        # Aquí, deberías realizar una consulta SQL para insertar los datos en la tabla de ingresos
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO ingresos (id_usuario, motivo, monto, fecha) VALUES (%s, %s, %s, %s)', (user_id, motivo, monto, fecha))
        mysql.connection.commit()
        cur.close()

        flash('Ingreso registrado con éxito')
        
    return redirect(url_for('Ingresos'))

if __name__ == '__main__':
    app.run(port=3000, debug=True)

