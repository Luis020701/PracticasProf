"""Con las librerias siguientes importo funcionalidades de flask y 
el redireccionamiento a templates con render_template"""
import sys
import os
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(BASE_DIR)
from Controlador.ValidarLogin import ValidarLogin
from flask import Flask,render_template, request, redirect, url_for, session,flash, jsonify
from flask_mysqldb import MySQL
from Config import Config
from decimal import Decimal, InvalidOperation
from Controlador.AltaHerramientas import AltaHerramientas
from Controlador.BuscarH import BuscarH
from Controlador.Movimientos import Movimientos
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
            flash('Insercion correcta', 'success')#mando un mensaje de exito a la plantilla html
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
    """Funcion para editar los datos de la herramienta"""
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
            precioh = Decimal(precioh_raw) if precioh_raw else Decimal('0')#Intento hacer la conversiona decimal y si no
        except InvalidOperation:
            flash('Precio inválido. Por favor ingresa un número válido.', 'error')#Retorno un error
            return render_template("RegistrarHerramienta.html")
        ediH= AltaHerramientas()
        ok, valor= ediH.editah(nombreh,tipoh,brandh,modeloh,serieh,codigoinh,statush,localidadh,responsableh,precioh,observacionesh)
        if not ok:
            flash(valor,'danger')
            return render_template('EditarHerramienta.html', datos=None)
        else:
            flash('Actualizacion de datos Exitosa!','success')
            return render_template('EditarHerramienta.html', datos=None)
    else:
        codigoinh= request.args.get('codigoinh','').strip()
        if codigoinh == '':
            return render_template('EditarHerramienta.html', datos=None)
        edi=AltaHerramientas()
        ok, valor = edi.cargardatos(codigoinh)
        if not ok:
            flash(valor,'danger')
            return render_template('EditarHerramienta.html', datos = None)
        else:
            flash('Herramienta Encontrada!','info')
            return render_template('EditarHerramienta.html', datos=valor)#Renderizo la pagina y envio los datos actuales
@Inv.route('/Buscarh')
def Buscarh():
    return render_template('BuscadorHerramienta.html')
@Inv.route('/api/Buscar')
def api_Buscar():
    termino = request.args.get('q','').strip()
    bus=BuscarH()
    ok,valor = bus.Buscarhe(termino,termino)
    if not ok:
        flash(valor,'danger')
        return jsonify({'error': valor}), 500
    else:
        return jsonify(valor)
@Inv.route('/entrasale', methods=['GET', 'POST'])
def entrasale():
    if request.method == 'POST':
        nombrea = request.form.get('nombrea', '').strip()
        nombrer = request.form.get('nombreR', '').strip()

        localidades = request.form.getlist('locala[]')
        herramientas = request.form.getlist('herra[]')
        acciones = request.form.getlist('acciona[]')
        observaciones = request.form.getlist('observacionesa[]')
        """El bloque anterior me sirve para obtener las listas con getlist ya que permite obtener varias herramientas"""

        mov = Movimientos()#creo mi variable para comunicarme con la funcion

        for i in range(len(herramientas)):#recorremos las herramientas con un for ya que son listas y esto me permite realizar todas las inserciones
            locala = localidades[i].strip()
            Cherra = herramientas[i].strip()
            acciona = acciones[i].strip()#limpiamos los campos para evitar espacios vacios
            obsa = observaciones[i].strip()

            if not Cherra:  # Evita procesar herramientas vacías, cada iteracion del for me permite obtener la herramienta depende la vuelta i
                continue

            ok, estado_actual = mov.estatusMov(Cherra)#esta funcion verifica en que estado se encuentra(entrada o salida)

            if not ok:#si no tiene estado
                ok, mensaje = mov.mov(nombrea, nombrer, locala, acciona, obsa, Cherra)#realiza el cambio de estado
                if not ok:#muestra en mensaje con flash segun sea el caso
                    flash(f"{Cherra}: {mensaje}", 'danger')
                else:
                    flash(f"{Cherra}: {mensaje}", 'success')
            else:
                if estado_actual == acciona:#esta parte del codigo meramente personaliza el msj que mostrara depende la accion que tiene
                    if estado_actual == "entrada":
                        flash(f"{Cherra}: Esta herramienta ya está en almacén", 'info')
                    elif estado_actual == "salida":
                        flash(f"{Cherra}: Esta herramienta ya está en préstamo", 'info')
                else:
                    ok, mensaje = mov.mov(nombrea, nombrer, locala, acciona, obsa, Cherra)#en caso de que no sea identica la accion
                    if not ok:#hace el cambio de accion y segun sea el caso muestra error o exito
                        flash(f"{Cherra}: {mensaje}", 'danger')
                    else:
                        flash(f"{Cherra}: {mensaje}", 'success')

        return render_template('EntradaSalida.html')

    return render_template('EntradaSalida.html')
@Inv.route('/logout')
def logout():
    """Funcion para cerrar la sesion activa"""
    session.clear()
    return redirect(url_for('login'))
if __name__=='__main__':
    Inv.config.from_object(Config['development'])
    Inv.run(debug=True)
