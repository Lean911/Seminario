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


@app.route('/inicio')
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


if __name__ == '__main__':
    app.run(port=3000, debug=True)

