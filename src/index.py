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
from decimal import Decimal, InvalidOperation
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
        oku,valoru = validador.validaruser(user)
        okp, valorp = validador.validapswd(passw,user)
        okon, datos = validador.obtenernombre(user)
        if not oku:#validamos si hay conexion a la db
            print("error")
            flash(valoru,'danger')#enviamos el error de la falta de conexion
            return render_template('auth/Login.html')#renderizamos la pagina de login
        else:
            if valoru is None :
                print("error usuario")
                flash('Error de usuario!', 'danger')#mando un mensaje de error a la plantilla html
                return render_template('auth/Login.html')
            
            elif not okp:
                print("error")
                flash(valorp,'danger')#enviamos el error de la falta de conexion
                return render_template('auth/Login.html')#renderizamos la pagina de login   
            elif not valorp:
                print("error contraseña")
                flash('Error de contraseña!', 'danger')#mando un mensaje de error a la plantilla html
                return render_template('auth/Login.html')
            else:
                if not okon:
                    print("error ")
                    flash(datos, 'danger')#mando un mensaje de error a la plantilla html
                    return render_template('auth/Login.html')
                else:
                    session['User']=datos[1]#recupero el user
                    session['nombre']=datos[3]#recupero el nombre
                    session['rol']=datos[4]#recupero el nombre
                    #y los mando a la sesion redireccionando a index
                    return render_template('index.html')

    else:
        #Si no, significa que es GET y renderiza la plantilla Login.html"""
        return render_template('auth/Login.html')
@Inv.route('/regisherra', methods=['GET', 'POST'])
def regisherra():
    """Metodo que registra las herramientas en BD"""
    if request.method == 'POST':
         
        nombreh = request.form.get('nombreh', '').strip()
        tipoh = request.form.get('tipoh', '').strip()
        brandh = request.form.get('brandh', '').strip()
        modeloh = request.form.get('modeloh', '').strip()
        serieh = request.form.get('serieh', '').strip()
        codigoinh = request.form.get('codigoinh', '').strip() or None
        statush = request.form.get('statush', '').strip()
        localidadh = request.form.get('localidadh', '').strip()
        responsableh = request.form.get('responsableh', '').strip()
        precioh = Decimal(request.form.get('precioh','').strip())
        observacionesh = request.form.get('observacionesh', '').strip()
        precioh_raw = request.form.get('precioh', '').strip()

        try:
            precioh = Decimal(precioh_raw) if precioh_raw else Decimal('0')
        except InvalidOperation:
            flash('Precio inválido. Por favor ingresa un número válido.', 'error')
            return render_template("RegistrarHerramienta.html")
        alta = AltaHerramientas()
        ok, valor = alta.altah(nombreh,tipoh,brandh,modeloh,serieh,codigoinh,statush,localidadh,responsableh,precioh,observacionesh)
        if not ok:
            print("error")
            flash(valor,'error')#enviamos el error de la falta de conexion
            return render_template("RegistrarHerramienta.html")
        elif valor:
            flash('Insercion correcta', 'info')#mando un mensaje de exito a la plantilla html
            return render_template("RegistrarHerramienta.html", modo='Crear')
    else: 
        #Si no es get renderizo la pagina de registro
        return render_template("RegistrarHerramienta.html", modo='Crear')
@Inv.route('/EliHerra', methods=['GET', 'POST'])
def EliHerra():
    """Este metodo Funciona para Eliminar una herramienta de el inventario"""
    if request.method=='POST':
        codiin= request.form.get('codigoinh')
        elimi = AltaHerramientas()
        ok, valor = elimi.eliminarh(codiin)
        if not ok:
            flash(valor, 'danger')
            return render_template('EliminarHerramienta.html')
        else:
            flash('Eliminado con exito','info')
            return render_template('EliminarHerramienta.html')
    else:
        return render_template('EliminarHerramienta.html')
@Inv.route('/EdiHerra', methods=['GET', 'POST'])
def EdiHerra():
    if request.method == 'POST':
        pass
    else:
        return render_template('EditarHerramienta.html')
@Inv.route('/logout')
def logout():
    """Funcion para cerrar la sesion activa"""
    session.clear()
    return redirect(url_for('login'))
if __name__=='__main__':
    Inv.config.from_object(Config['development'])
    Inv.run(debug=True)
