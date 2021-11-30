from flask import Flask, render_template, request, redirect, url_for, flash, session, logging
from flask_mysqldb import MySQL
import os, pymysql
from dotenv import load_dotenv, find_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_bcrypt import Bcrypt
# Load Enviroment Variables from .env file
load_dotenv(find_dotenv())

# initializations
app = Flask(__name__)

bcrypt = Bcrypt(app)

# Mysql Connection
app.config['MYSQL_HOST'] = os.getenv('dbHOST')
app.config['MYSQL_USER'] = os.getenv('dbUSER')
app.config['MYSQL_PASSWORD'] = os.getenv('dbPASSWORD')
app.config['MYSQL_DB'] = os.getenv('dbNAME')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


mysql = MySQL(app)

# settings
app.secret_key = "mysecretkey"

# routes
@app.route('/')
def PagiP():
    return render_template('Pagina-principal.html')

# Check if Admin is logged-in
def admin_is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'admin_logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('No estás autorizado, Ingrese a su cuenta', 'error')
            return redirect(url_for('loginAdmin'))
    return wrap

# Modulo Administration
@app.route('/admin')
@admin_is_logged_in
def admin():
    return render_template('admin.html')

@app.route('/add_user', methods=['POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['firstName']
        lastName = request.form['lastName']
        idNumber = str(request.form['idNumber'])
        rol = request.form['rol']
        username = request.form['username']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO `Modulo administración` (Nombres,Apellidos,Cédula,Rol,Usuario,Contraseña) VALUES(%s,%s,%s,%s,%s,%s)',
        (name,lastName,idNumber,rol,username,password))
        mysql.connection.commit()

        flash('Usuario Ingresado Exitosamente')
        return redirect(url_for('PagiP'))

@app.route('/login_admin', methods=['GET','POST'])
def loginAdmin():
    if request.method == 'POST':
        # Get form Fields
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()

        # Get user by username
        user_db = cur.execute('SELECT * FROM Admins WHERE Usuario = %s',
        [username])

       # Compare Passwords
        if user_db > 0:
            user_db = cur.fetchone()
            user_pass = user_db['Contraseña']

            if password == user_pass:
                session['admin_logged_in'] =  True
                session['admin_username'] = username

                flash('¡Bienvenido Administrador/a')
                return redirect(url_for('admin'))
            else:
                flash('Contraseña Incorrecta, intente nuevamente.','error')
        else:
            flash('Este admin no existe.','error')
    return render_template("login-admin.html")


# END Modulo Administration
# Modulo Logout Administrador
@app.route('/logout')
def logout():
    session.clear()
    flash('Te has Salío de la cuenta exitosamente.')
    return redirect(url_for('PagiP'))

# Modulo Registro caso
@app.route('/registro')
def registro():
    return render_template('registro.html')


@app.route('/add_case', methods=['POST'])
def add_case():
    if request.method == 'POST':
        name = request.form['firstName']
        lastName = request.form['lastName']
        idNumber = str(request.form['idNumber'])
        Sexo = request.form['Sexo']
        FechaNacimiento = request.form['Fecha de nacimiento']
        DireccionResidencia = request.form['Direccion de residencia']
        DireccionTrabajo = request.form['Direccion trabajo']
        ResultadoExamen = request.form['ResultadoExamen']
        FechaExamen = request.form['Fecha examen']

        
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO `Registro de Caso` (Nombres,Apellidos,Cédula,Sexo,Fecha de nacimiento,Dirección de residencia,Dirección Trabajo,Resultado Examen,Fecha examen) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)',
        (name,lastName,idNumber,Sexo,FechaNacimiento,DireccionResidencia,DireccionTrabajo,ResultadoExamen,FechaExamen))
        mysql.connection.commit()

        return redirect(url_for('registroSuccess'))


@app.route('/registroSuccess')
def registroSuccess():
    return render_template('registro-Success.html')
# END Modulo Registro Caso

#Modulo Visualización
@app.route('/Visual')
def Visual():
    return render_template('Mapa.html')
# END Modulo Visualización

# Modulo Busqueda
@app.route('/Gestionar')
def editar():
    return render_template('Gestion.html')
# END Modulo Busqueda

#Log in
@app.route('/Login')
def Login():
    return render_template('Login.html')
#End Log in

"""@app.route('/edit/<id>', methods = ['POST', 'GET'])
def get_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM contacts WHERE id = %s', (id))
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('edit-contact.html', contact = data[0])

@app.route('/delete/<string:id>', methods = ['POST','GET'])
def delete_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM contacts WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('Contact Removed Successfully')
    return redirect(url_for('Index'))"""

# starting the app
if __name__ == "__main__":
    app.run(port=3000, debug=True)