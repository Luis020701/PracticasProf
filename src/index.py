"""Con las librerias siguientes importo funcionalidades de flask y 
el redireccionamiento a templates con render_template"""
#librerias estandar
from datetime import datetime
from decimal import Decimal, InvalidOperation
#librerias externas
import sys
import os
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(BASE_DIR)
from flask import Flask,render_template, request, redirect, url_for, session,flash, jsonify, send_file, make_response
from Config import Config
from weasyprint import HTML, CSS
from functools import wraps
#modulos proyecto
from Controlador.AltaHerramientas import AltaHerramientas
from Controlador.BuscarH import BuscarH
from Controlador.Movimientos import Movimientos
from Controlador.Historial import Historial
from Controlador.ValidarLogin import ValidarLogin

Inv = Flask(__name__)
Inv.secret_key ="cookies_1_2.3.4_5_6"

def login_required(f):
    """me permite validar el atributo User para validar el inicio de sesion"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "User" not in session:
            flash("Debes iniciar sesión para acceder a esta página",'danger')
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

"""La ruta me sirve para redireccionar a la ruta de login al ser la primera"""
@Inv.route('/')
@login_required
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
                #mando un mensaje de error a la plantilla html
                flash('Error de contraseña!', 'danger')
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
@login_required
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
        ok, valor = alta.altah(
            nombreh,tipoh,brandh,modeloh,serieh,
            codigoinh,
            statush,localidadh,responsableh,
            precioh,observacionesh
            )
        if not ok:
            print("error")
            flash(valor,'error')#enviamos el error de la falta de conexion
            return render_template("RegistrarHerramienta.html")
        if valor:
            flash('Insercion correcta', 'success')#mando un mensaje de exito a la plantilla html
            return render_template("RegistrarHerramienta.html", modo='Crear')
    else:
        #Si no es get renderizo la pagina de registro
        return render_template("RegistrarHerramienta.html", modo='Crear')
@Inv.route('/eliminar_herramienta', methods=['GET', 'POST'])
@login_required
def eliminar_herramienta():
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
@Inv.route('/editar_herramienta', methods=['GET', 'POST'])
@login_required
def editar_herramienta():
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
            #Intento hacer la conversiona decimal y si no
            precioh = Decimal(precioh_raw) if precioh_raw else Decimal('0')
        except InvalidOperation:
            flash('Precio inválido. Por favor ingresa un número válido.', 'error')#Retorno un error
            return render_template("RegistrarHerramienta.html")
        edih= AltaHerramientas()
        ok, valor= edih.editah(
            nombreh,tipoh,brandh,modeloh,serieh,codigoinh,statush,
            localidadh,responsableh,
            precioh,observacionesh)
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
            #Renderizo la pagina y envio los datos actuales
            return render_template('EditarHerramienta.html', datos=valor)
@Inv.route('/buscar_herramienta', methods=['GET', 'POST'])
@login_required
def buscar_herramienta():
    """funcion que meramente sirve para renderizar la pagina del buscador"""
    return render_template('BuscadorHerramienta.html')
@Inv.route('/api/Buscar')
@login_required
def api_buscar():
    """Esta Funcion me permite ejecutar la busqueda parcial 
    por medio de los argumentos que obtiene constantemente"""
    termino = request.args.get('q','').strip()
    bus=BuscarH()
    ok,valor = bus.Buscarhe(termino,termino)
    if not ok:
        flash(valor,'danger')
        return jsonify({'error': valor}), 500
    else:
        return jsonify(valor)
@Inv.route('/entra_sale', methods=['GET', 'POST'])
@login_required
def entra_sale():
    """Esta funciom detecte el tipo de movimiento que se quiere realizar"""
    if request.method == 'POST':
        nombrea = request.form.get('nombrea', '').strip()
        nombrer = request.form.get('nombreR', '').strip()

        localidades = request.form.getlist('locala[]')
        herramientas = request.form.getlist('herra[]')
        acciones = request.form.getlist('acciona[]')
        observaciones = request.form.getlist('observacionesa[]')
        #El bloque anterior me sirve para obtener las listas con getlist
        # ya que permite obtener varias herramientas
        mov = Movimientos()#creo mi variable para comunicarme con la funcion
        for i in enumerate(herramientas):
            #recorremos las herramientas con un for ya que son listas y
            # esto me permite realizar todas las inserciones
            locala = localidades[i].strip()
            cherra = herramientas[i].strip()
            acciona = acciones[i].strip()#limpiamos los campos para evitar espacios vacios
            obsa = observaciones[i].strip()

            if not cherra:
                # Evita procesar herramientas vacías,
                # cada iteracion del for me permite obtener la herramienta depende la vuelta i
                continue

            ok, estado_actual = mov.estatusMov(cherra)
            #esta funcion verifica en que estado se encuentra(entrada o salida)

            if not ok:#si no tiene estado
                estatus_invalidos = ['en_reparacion', 'extraviada', 'obsoleta']
                if estado_actual in estatus_invalidos:
                    flash(f"El estatus es:{estado_actual}",'danger')
                else:
                    ok, mensaje = mov.mov(nombrea, nombrer, locala, acciona, obsa, cherra)
                    #realiza el cambio de estado
                    if not ok:
                        #muestra en mensaje con flash segun sea el caso
                        flash(f"{cherra}: {mensaje}", 'danger')
                    else:
                        flash(f"{cherra}: {mensaje}", 'success')
            else:
                if estado_actual == acciona:
                    #esta parte del codigo meramente personaliza el msj que mostrara,
                    #dependiendo la accion que tiene
                    if estado_actual == "entrada":
                        flash(f"{cherra}: Esta herramienta ya está en almacén", 'info')
                    elif estado_actual == "salida":
                        flash(f"{cherra}: Esta herramienta ya está en préstamo", 'info')
                else:
                    ok, mensaje = mov.mov(nombrea, nombrer, locala, acciona, obsa, cherra)
                    #en caso de que no sea identica la accion
                    if not ok:
                        #hace el cambio de accion y segun sea el caso muestra error o exito
                        flash(f"{cherra}: {mensaje}", 'danger')
                    else:
                        flash(f"{cherra}: {mensaje}", 'success')

        return render_template('EntradaSalida.html')

    return render_template('EntradaSalida.html')
@Inv.route('/historial', methods=['GET','POST'])
@login_required
def historial():
    """este metodo me permite obtener el historial y compartirlo a la vista html"""
    filtros = {  # inicializamos siempre
        "nombrer": "",
        "herra": "",
        "accion": "",
        "fechaini": "",
        "fechafin": ""
    }
    if request.method=='POST':
        filtros = {
            "nombrer" : request.form.get('nombreR','').strip(),
            "herra" : request.form.get('herra','').strip(),
            "accion" : request.form.get('accion','').strip(),
            "fechaini" : request.form.get('fechaini','').strip(),
            "fechafin" : request.form.get('fechafin','').strip(),
        }
        if not filtros:
            flash("Debes ingresar al menos un parametro", 'warning')
            return render_template('Historial.html')
        #Creo un arreglo para poder ir añadiendo las condiciones y los valores segun sea el caso
        valor = []
        condicion = []
        #En cada caso valido si el usuario introdujo algun valor,
        # en caso de que no, no inserto nada al arreglo """
        if filtros["nombrer"]:
            condicion.append("person = %s")
            valor.append(filtros["nombrer"])
        if filtros["accion"]:
            condicion.append("action = %s")
            valor.append(filtros["accion"])
        if filtros["fechaini"]:
            condicion.append("timestamp >= %s")
            valor.append(filtros["fechaini"])
        if filtros["fechafin"]:
            condicion.append("timestamp <= %s")
            valor.append(filtros["fechafin"])
        histo = Historial()
        ok,valores= histo.histo(filtros["herra"],condicion,valor)
        if not ok:
            flash(valores,'danger')#enviamos el error que nos regrese
            return render_template('Historial.html',filtros=filtros)
        else:
            return render_template('Historial.html', datos=valores, filtros=filtros)
    else:
        return render_template('Historial.html', filtros=filtros)
@Inv.route('/reporte', methods=['GET','POST'])
@login_required
def reporte():
    nombrer = request.form.get('nombreR','').strip()
    herra = request.form.get('herra','').strip()
    accion = request.form.get('accion','').strip()
    fechaini = request.form.get('fechaini','').strip()
    fechafin = request.form.get('fechafin','').strip()

    if not (nombrer or herra or accion or fechaini or fechafin):
        flash("Debes ingresar al menos un parametro", 'warning')
        return render_template('Historial.html', filtros=[])

    valor = []
    condicion= []

    if nombrer:
        condicion.append("person = %s")
        valor.append(nombrer)
    if accion:
        condicion.append("action = %s")
        valor.append(accion)
    if fechaini:
        condicion.append("timestamp >= %s")
        valor.append(fechaini)
    if fechafin:
        condicion.append("timestamp <= %s")
        valor.append(fechafin)

    histo = Historial()
    ok, valores = histo.histo(herra, condicion, valor)
    if not ok:
        flash("No se ha podido generar el reporte", 'warning')
        return render_template('Historial.html',filtros=[])
    else:
        # Renderizar HTML para PDF
        html = render_template("ReporteHistorial.html", datos=valores)

        # Ruta absoluta a la carpeta src
        base_dirs = os.path.abspath(os.path.join(os.path.dirname(__file__)))

        # CSS absoluto
        css_path = os.path.join(base_dirs, "static", "css", "styleTemplate.css")

        # PDF con base_url = carpeta src
        pdf = HTML(string=html, base_url=base_dirs).write_pdf(
            stylesheets=[CSS(css_path)]
        )

        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=reporte.pdf'
        return response
@Inv.route('/logout')
def logout():
    """Funcion para cerrar la sesion activa"""
    session.clear()
    return redirect(url_for('login'))
if __name__=='__main__':
    Inv.config.from_object(Config['development'])
    Inv.run(debug=True)
