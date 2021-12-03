from flask import Flask, render_template, request, redirect, url_for, flash, session, logging
from flask_mysqldb import MySQL
import os, pymysql
from dotenv import load_dotenv, find_dotenv
from requests.exceptions import RequestsWarning
from requests.models import LocationParseError
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_bcrypt import Bcrypt
import requests
from matplotlib import pyplot as plt
import numpy as np
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
# Modulo Login Ayudante (Registro de Caso)
@app.route('/login_ayudante', methods=['GET','POST'])
def loginAyudante():
    if request.method == 'POST':
        # Get form Fields
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()

        # Get user by username
        user_db = cur.execute('SELECT * FROM `Modulo administración` WHERE Usuario = %s AND Rol="1"',
        [username])

       # Compare Passwords
        if user_db > 0:
            user_db = cur.fetchone()
            user_pass = user_db['Contraseña']

            if password == user_pass:
                session['ayudante_logged_in'] =  True
                session['ayudante_username'] = username

                return redirect(url_for('mainAyudante'))
            else:
                flash('Contraseña Incorrecta, intente nuevamente.','error')
        else:
            flash('Este ayudante no existe.','error')
    return render_template("login-ayudante.html")

# Check if Ayudante is logged-in
def ayudante_is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'ayudante_logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('No estás autorizado, Ingrese a su cuenta', 'error')
            return redirect(url_for('loginAyudante'))
    return wrap

# Modulo Inicio de Ayudante (Donde se le muestran las 2 opciones)
@app.route('/main_ayudante')
@ayudante_is_logged_in
def mainAyudante():
    return render_template('main-ayudante.html')


# Modulo Login Médico (Registro de Caso)
@app.route('/login_medico', methods=['GET','POST'])
def loginMedico():
    if request.method == 'POST':
        # Get form Fields
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()

        # Get medico by username
        user_db = cur.execute('SELECT * FROM `Modulo administración` WHERE Usuario = %s AND Rol="2"',
        [username])

       # Compare Passwords
        if user_db > 0:
            user_db = cur.fetchone()
            user_pass = user_db['Contraseña']

            if password == user_pass:
                session['medico_logged_in'] =  True
                session['medico_username'] = username

                return redirect(url_for('mainMedico'))
            else:
                flash('Contraseña Incorrecta, intente nuevamente.','error')
        else:
            flash('Este médico no existe.','error')
    return render_template("login-medico.html")

# Check if Médico is logged-in
def medico_is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'medico_logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('No estás autorizado, Ingrese a su cuenta', 'error')
            return redirect(url_for('loginMedico'))
    return wrap

# Modulo Inicio de Medico (Donde se le muestran las 2 opciones)
@app.route('/main_medico')
@medico_is_logged_in
def mainMedico():
    return render_template('main-medico.html')
# Modulo Logout 
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
    return render_template('mapa2.html')
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

#Request-map(residencia)
API_KEY='AIzaSyCCdzkkX62BwJVVZu5X4zs-b4OC1mgr6jU'
address = 'carrera 28 #22-53 malambo'
def getGeoCoord(address):
        params= {
            'key': API_KEY,
            'address' : address.replace(' ','+') #Direccion de residencia(base de datos)
        }

        base_url = 'https://maps.googleapis.com/maps/api/geocode/json?'

        response = requests.get(base_url, params=params).json()
        response.keys()
        print (response['status'])
        if response['status'] == 'OK':
            geometry = response['results'][0]['geometry']
            lat = geometry['location']['lat']
            lon = geometry['location']['lng']
            print (lat, lon)
            return (lat,lon)
        else:
            return  
getGeoCoord(address)

#Grafica de XY

p=1
def grafica1(p):
    if p>=1:
        dia=[1,2,3,4]
        numcasos=[1,4,10,12]
        muerte=[1,2,2,7]

        plt.title("Número de casos vs Número de Muertes",fontsize=15)
        plt.xlabel("Días",fontsize=13)
        plt.ylabel("Casos",fontsize=13)
        plt.subplot(221)
        plt.plot(dia,numcasos,color="green",markersize=10,marker="p",label="Número de casos")
        plt.plot(dia,muerte,color="red", markersize=10,marker="p",label="Número de muertes")
        plt.legend()
        #Grafica-pie1
        Estado = [10,3,20] #Colocar los valores de la base de datos
        nombres = ["Infectados","Muertes","Curados"]
        plt.subplot(222)
        plt.pie(Estado, labels=nombres, autopct="%0.1f %%")
        plt.axis("equal")
        #Grafica-pie2
        Estado = [10,5,4]#Valores de la base de datos
        nombres = ["En tratamiento en casa","en UCI","Fallecidos"]
        plt.subplot(223)
        plt.pie(Estado, labels=nombres, autopct="%0.1f %%")
        plt.axis("equal")
        #Grafica-pie3
        Estado = [10, 2]#valores 
        nombres = ["Valores positivos","valores negativos"]
        plt.subplot(224)
        plt.pie(Estado, labels=nombres, autopct="%0.1f %%")
        plt.axis("equal")
        plt.savefig('C:/Users/PC/Documents/Universidad/Covid/covid-tracker-telematica/static/img/Graficas.png')
        plt.show()
grafica1(p)
#Grafica pie1
#Crear en la base de datos los totales y que se cuenten
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