"""Con las librerias siguientes importo funcionalidades de flask y 
el redireccionamiento a templates con render_template"""
import sys
import os
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(BASE_DIR)
from Controlador.ValidarLogin import ValidarLogin
from flask import Flask,render_template, request, redirect, url_for, session,flash
from flask_mysqldb import MySQL
from Config import Config
from decimal import Decimal
from Controlador.AltaHerramientas import AltaHerramientas

Inv = Flask(__name__)
db=MySQL(Inv)
"""La ruta me sirve para redireccionar a la ruta de login al ser la primera"""
@Inv.route('/')
def index():
    """redirecciona a la ruta login si no hay una sesion abierta"""
    if 'User' not in session:
        return redirect(url_for('login'))
    else:
        return render_template('index.html')

@Inv.route('/login', methods=['GET', 'POST'])
def login():
    """La funcion sirve para validar el Login"""
    if request.method=='POST':
        #Si el metodo es POST: Significa que envio datos
        user=str(request.form['username']).strip()
        passw=str(request.form['password']).strip()
        validador = ValidarLogin()
        if validador.validaruser(user) is None :
            print("error usuario")
            flash('Error de usuario!', 'error')#mando un mensaje de error a la plantilla html
            return render_template('auth/Login.html')
        elif validador.validapswd(passw,user) is False: 
            print("error contraseña")
            flash('Error de contraseña!', 'error')#mando un mensaje de error a la plantilla html
            return render_template('auth/Login.html')
        else:
            session['User']=validador.obtenernombre(user)[1]#recupero el user
            session['nombre']=validador.obtenernombre(user)[3]#recupero el nombre
            session['rol']=validador.obtenernombre(user)[4]#recupero el nombre
            #y los mando a la sesion redireccionando a index
            validador.cerrarcursor()
            return render_template('index.html')
    else:
        #Si no, significa que es GET y renderiza la plantilla Login.html"""
        return render_template('auth/Login.html')
@Inv.route('/regisherra', methods=['GET', 'POST'])
def regisherra():
    """Metodo que registra las herramientas en BD"""
    if request.method == 'POST':
        nombreh = request.form['nombreh'].strip()
        tipoh = request.form['tipoh'].strip()
        brandh = request.form['brandh'].strip()
        modeloh = request.form['modeloh'].strip()
        serieh = request.form['serieh'].strip()
        codigoinh = request.form['codigoinh'].strip()
        statush = request.form['statush'].strip()
        localidadh = request.form['localidadh'].strip()
        responsableh = request.form['responsableh'].strip()
        precioh = Decimal(request.form['precioh'].strip())
        observacionesh = request.form['observacionesh'].strip()
        alta = AltaHerramientas()
        if alta.altah(nombreh,tipoh,brandh,modeloh,serieh,codigoinh,statush,localidadh,responsableh,precioh,observacionesh) is True:
            flash('Insercion correcta', 'info')#mando un mensaje de error a la plantilla html
            return render_template("RegistrarHerramienta.html")
    else: 
        #Si no es get renderizo la pagina de registro
        return render_template("RegistrarHerramienta.html")
@Inv.route('/logout')
def logout():
    """Funcion para cerrar la sesion activa"""
    session.clear()
    return redirect(url_for('login'))
if __name__=='__main__':
    Inv.config.from_object(Config['development'])
    Inv.run(debug=True)
