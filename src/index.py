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
from Controlador.Inventario import Inventario
from Controlador.AltaMochilas import AltaMochilas
from Controlador.AsignacionesPermanentes import AsignacionesPermanentes
from Controlador.MovimientosMochilas import MovimientosMochilas
from DataBase.Conexion import Conexion
Inv = Flask(__name__)
Inv.secret_key ="cookies_1_2.3.4_5_6"

#=============================
#ROLES DEL SISTEMA
#=============================
ROLES = {
    "Administrador":1,
    "Almacen":2,
    "Instalador":3
}
#=============================
#=============================
#DECORADORES PARA VALIDAR USUARIOS LOGUEADOS Y ROLES
#===================================================
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
    
def role_required(*roles):
    """Valida que el usuario tenga uno de los roles permitidos"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "User" not in session:
                flash("Debes iniciar sesión", "danger")
                return redirect(url_for("login"))

            if session.get("rol") not in roles:
                flash("No tienes permisos para acceder a esta sección", "danger")
                return redirect(url_for("index"))

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def es_instalador():
    """Indica si el usuario actual tiene permisos de instalador."""
    return session.get("rol") == ROLES["Instalador"]

#========================================================================================
#FUNCIÓN AUXILIAR PARA OBTENER USUARIOS
#========================================================================================
def obtener_usuarios():
    """Obtiene la lista de nombres de usuarios de la base de datos"""
    try:
        db = Conexion()
        ok, conn = db.conectar()
        if not ok:
            return []
        
        cur = conn.cursor(dictionary=True)
        sql = "SELECT full_name FROM user WHERE is_active = 1 ORDER BY full_name"
        cur.execute(sql)
        usuarios = [row['full_name'] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return usuarios
    except Exception as e:
        print(f"Error al obtener usuarios: {e}")
        return []

def obtener_codigos_herramientas():
    """Obtiene códigos de herramientas existentes y activas para autocompletado."""
    try:
        db = Conexion()
        ok, conn = db.conectar()
        if not ok:
            return []

        cur = conn.cursor(dictionary=True)
        sql = """
            SELECT internal_code, name
            FROM tools
            WHERE status <> 'eliminada'
              AND internal_code IS NOT NULL
              AND internal_code <> ''
            ORDER BY internal_code
        """
        cur.execute(sql)
        herramientas = cur.fetchall()
        cur.close()
        conn.close()
        return herramientas
    except Exception as e:
        print(f"Error al obtener herramientas: {e}")
        return []

def obtener_codigos_mochilas():
    """Obtiene códigos de mochilas/kits activos para autocompletado."""
    try:
        db = Conexion()
        ok, conn = db.conectar()
        if not ok:
            return []

        cur = conn.cursor(dictionary=True)
        sql = """
            SELECT internal_code, nombre
            FROM mochilas
            WHERE activo <> 0
              AND internal_code IS NOT NULL
              AND internal_code <> ''
            ORDER BY internal_code
        """
        cur.execute(sql)
        mochilas = cur.fetchall()
        cur.close()
        conn.close()
        return mochilas
    except Exception as e:
        print(f"Error al obtener mochilas: {e}")
        return []

def obtener_valores_distintos(tabla, columna, condicion="1=1"):
    """Obtiene valores únicos de una columna para catálogos de autocompletado."""
    try:
        db = Conexion()
        ok, conn = db.conectar()
        if not ok:
            return []

        cur = conn.cursor()
        sql = f"""
            SELECT DISTINCT {columna}
            FROM {tabla}
            WHERE {condicion}
              AND {columna} IS NOT NULL
              AND {columna} <> ''
            ORDER BY {columna}
        """
        cur.execute(sql)
        valores = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return valores
    except Exception as e:
        print(f"Error al obtener catálogo {tabla}.{columna}: {e}")
        return []

def obtener_catalogos_autocompletado():
    """Agrupa catálogos usados por los formularios para sugerencias."""
    usuarios = obtener_usuarios()
    herramientas = obtener_codigos_herramientas()
    mochilas = obtener_codigos_mochilas()

    ubicaciones = sorted(set(
        obtener_valores_distintos("tools", "location", "status <> 'eliminada'")
        + obtener_valores_distintos("movements", "location")
        + obtener_valores_distintos("mochilas", "localidad", "activo <> 0")
    ))
    responsables = sorted(set(
        usuarios
        + obtener_valores_distintos("tools", "responsible", "status <> 'eliminada'")
        + obtener_valores_distintos("movements", "person")
        + obtener_valores_distintos("mochilas", "responsable", "activo <> 0")
    ))

    return {
        "usuarios": usuarios,
        "responsables": responsables,
        "herramientas": herramientas,
        "mochilas": mochilas,
        "nombres_herramientas": obtener_valores_distintos("tools", "name", "status <> 'eliminada'"),
        "tipos_herramientas": obtener_valores_distintos("tools", "tool_type", "status <> 'eliminada'"),
        "marcas_herramientas": obtener_valores_distintos("tools", "brand", "status <> 'eliminada'"),
        "modelos_herramientas": obtener_valores_distintos("tools", "model", "status <> 'eliminada'"),
        "series_herramientas": obtener_valores_distintos("tools", "serial_number", "status <> 'eliminada'"),
        "nombres_mochilas": obtener_valores_distintos("mochilas", "nombre", "activo <> 0"),
        "ubicaciones": ubicaciones,
    }

@Inv.context_processor
def inyectar_catalogos_autocompletado():
    """Hace disponibles los catálogos en todas las plantillas."""
    return {"autocompletar": obtener_catalogos_autocompletado()}

def obtener_mi_inventario(nombre_usuario):
    """Obtiene herramientas y mochilas asignadas al usuario en sesión."""
    db = Conexion()
    ok, conn = db.conectar()
    if not ok:
        return False, conn

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT
                t.internal_code,
                t.name,
                t.brand,
                t.model,
                t.status,
                t.location,
                lm.timestamp AS assigned_at,
                'Herramienta' AS item_type
            FROM tools t
            JOIN (
                SELECT m1.tool_id, m1.person, m1.action, m1.timestamp
                FROM movements m1
                JOIN (
                    SELECT tool_id, MAX(timestamp) AS max_ts
                    FROM movements
                    GROUP BY tool_id
                ) latest ON latest.tool_id = m1.tool_id AND latest.max_ts = m1.timestamp
            ) lm ON lm.tool_id = t.id
            WHERE t.status <> 'eliminada'
              AND lm.action = 'salida'
              AND lm.person = %s
            ORDER BY lm.timestamp DESC
        """, (nombre_usuario,))
        herramientas = cur.fetchall()

        cur.execute("""
            SELECT
                internal_code,
                nombre,
                descripcion,
                estado,
                localidad,
                responsable,
                'Mochila/Kit' AS item_type
            FROM mochilas
            WHERE activo <> 0
              AND responsable = %s
            ORDER BY nombre
        """, (nombre_usuario,))
        mochilas = cur.fetchall()

        return True, {"herramientas": herramientas, "mochilas": mochilas}
    except Exception as e:
        return False, str(e)
    finally:
        cur.close()
        conn.close()

def prestar_mochila_completa(codigo_mochila, responsable, localidad):
    """Registra el préstamo de una mochila completa a un responsable."""
    db = Conexion()
    ok, conn = db.conectar()
    if not ok:
        return False, conn

    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE mochilas
            SET estado = 'prestada', responsable = %s, localidad = %s
            WHERE internal_code = %s AND activo <> 0
        """, (responsable, localidad, codigo_mochila))
        if cur.rowcount == 0:
            conn.rollback()
            return False, "No se encontró la mochila o está inactiva"
        conn.commit()
        return True, "Préstamo de mochila registrado correctamente"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()

#========================================================================================

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
@role_required(ROLES['Administrador'], ROLES['Almacen'])
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
            return render_template("RegistrarHerramienta.html", usuarios=obtener_usuarios())
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
            return render_template("RegistrarHerramienta.html", usuarios=obtener_usuarios())
        if valor:
            mov = Movimientos()
            user_name = session.get('nombre','')
            ok_log, log_msg = mov.mov(user_name, responsableh, localidadh, 'alta', 'Alta de herramienta', codigoinh)
            if not ok_log:
                flash(f'Atención: no se pudo registrar el historial de alta ({log_msg})', 'warning')
            flash('Insercion correcta', 'success')#mando un mensaje de exito a la plantilla html
            return render_template("RegistrarHerramienta.html", modo='Crear', usuarios=obtener_usuarios())
    else:
        #Si no es get renderizo la pagina de registro
        return render_template("RegistrarHerramienta.html", modo='Crear', usuarios=obtener_usuarios())  
@Inv.route('/regis_kit', methods=['GET', 'POST'])
@login_required
@role_required(ROLES['Administrador'], ROLES['Almacen'])
def regis_kit():
    """
    Esta funcion permite la creacion de mochilas o kits de herramientas
    """
    if request.method == 'POST':
        estados_disponibles= ('disponible', 'prestada', 'parcial')
        nombre_kit = request.form.get('nombre_kit','').strip()
        respos_kit = request.form.get('respos_kit','').strip()
        status_kit = request.form.get('status_kit','').strip()
        descripcion_kit = request.form.get('descripcion_kit','').strip()
        codigoi = request.form.get('codigo_kit','').strip()
        
        if status_kit not in estados_disponibles:
            flash('Error, El status no es correcto','error')
            return render_template("Mochilas.html", usuarios=obtener_usuarios())
        alta_m = AltaMochilas()
        ok, resultado = alta_m.registro_kit(nombre_kit,respos_kit,status_kit,descripcion_kit,codigoi)
        if not ok:
            flash(resultado,'error')
            return render_template("Mochilas.html", usuarios=obtener_usuarios())
        else:
            flash(resultado,'success')
            return render_template("Mochilas.html", usuarios=obtener_usuarios())
    else:
        return render_template("Mochilas.html", usuarios=obtener_usuarios())
@Inv.route('/eliminar_herramienta', methods=['GET', 'POST'])
@login_required
@role_required(ROLES['Administrador'], ROLES['Almacen'])
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
@Inv.route('/eliminar_KM', methods=['GET', 'POST'])
@login_required
@role_required(ROLES['Administrador'], ROLES['Almacen'])
def eliminar_KM():
    """Este metodo Funciona para Eliminar una mochila o kit de el inventario"""
    if request.method=='POST':
        codiin= request.form.get('codigo_KM')
        print("Codigo Interno de la Mochila/Kit a eliminar:", codiin)
        elimi = AltaMochilas()
        ok, valor = elimi.eliminar_KM(codiin)
        if not ok:
            flash(valor, 'danger')
            return render_template('eliminarMochila.html', mochilas=obtener_codigos_mochilas())
        else:
            flash('Eliminado con exito','info')
            return render_template('eliminarMochila.html', mochilas=obtener_codigos_mochilas())
    else:
        return render_template('eliminarMochila.html', mochilas=obtener_codigos_mochilas())
@Inv.route('/editar_herramienta', methods=['GET', 'POST'])
@login_required
@role_required(ROLES['Administrador'], ROLES['Almacen'])
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
            return render_template("RegistrarHerramienta.html", usuarios=obtener_usuarios())
        edih= AltaHerramientas()
        old_ok, old_data = edih.cargardatos(codigoinh)
        old_responsable = old_data['responsible'] if old_ok and isinstance(old_data, dict) else None

        ok, valor= edih.editah(
            nombreh,tipoh,brandh,modeloh,serieh,codigoinh,statush,
            localidadh,responsableh,
            precioh,observacionesh)
        if not ok:
            flash(valor,'danger')
            return render_template('EditarHerramienta.html', datos=None, usuarios=obtener_usuarios())
        else:
            user_name = session.get('nombre','')
            user_rol = session.get('rol')
            marcar_permanente = request.form.get('marcar_permanente', '').strip().lower() == 'on'

            if old_ok and old_responsable and old_responsable != responsableh:
                mov = Movimientos()
                ok_log, log_msg = mov.mov(user_name, responsableh, localidadh, 'cambio de propietario', f'Cambio de propietario de {old_responsable} a {responsableh}', codigoinh, rol=user_rol)
                if not ok_log:
                    flash(f'Atención: {log_msg}', 'warning')
                else:
                    if marcar_permanente:
                        asig_perm = AsignacionesPermanentes()
                        ok_perm, msg_perm = asig_perm.marcar_asignacion_permanente(codigoinh, responsableh, 'auto', user_name)
                        if ok_perm:
                            flash(f'{msg_perm}', 'success')
                        else:
                            flash(f'Advertencia: {msg_perm}', 'warning')
            elif marcar_permanente:
                asig_perm = AsignacionesPermanentes()
                ok_perm, msg_perm = asig_perm.marcar_asignacion_permanente(codigoinh, responsableh, 'auto', user_name)
                if ok_perm:
                    flash(f'{msg_perm}', 'success')
                else:
                    flash(f'Advertencia: {msg_perm}', 'warning')

            flash('Actualizacion de datos Exitosa!','success')
            return render_template('EditarHerramienta.html', datos=None, usuarios=obtener_usuarios())
    else:
        codigoinh= request.args.get('codigoinh','').strip()
        if codigoinh == '':
            return render_template('EditarHerramienta.html', datos=None, usuarios=obtener_usuarios())
        edi=AltaHerramientas()
        ok, valor = edi.cargardatos(codigoinh)
        if not ok:
            flash(valor,'danger')
            return render_template('EditarHerramienta.html', datos = None, usuarios=obtener_usuarios())
        else:
            flash('Herramienta Encontrada!','info')
            #Renderizo la pagina y envio los datos actuales
            return render_template('EditarHerramienta.html', datos=valor, usuarios=obtener_usuarios())
@Inv.route('/editar_KM', methods=['GET', 'POST'])
@login_required
@role_required(ROLES['Administrador'], ROLES['Almacen'])
def editar_KM():
    """Funcion para editar los datos de la mochila o kit"""
    if request.method == 'POST':
        nombre_KM = request.form.get('nombre_KM','').strip()
        Respos_KM = request.form.get('Respos_KM','').strip()
        status_KM = request.form.get('status_KM','').strip()
        Descripcion_KM = request.form.get('Descripcion_KM','').strip()
        localidad_KM = request.form.get('localidad_KM','').strip()
        codigoi = request.form.get('codigo_KM','').strip()
        edi_KM= AltaMochilas()
        print(codigoi)
        ok , resultado = edi_KM.editar_KM(nombre_KM,Respos_KM,status_KM,Descripcion_KM,codigoi,localidad_KM)
        if not ok:
            flash(resultado,'error')
            return render_template('EditarMochila.html', datos=None, usuarios=obtener_usuarios(), mochilas=obtener_codigos_mochilas())
        else:
            flash(resultado,'success')
            return render_template('EditarMochila.html', datos=None, usuarios=obtener_usuarios(), mochilas=obtener_codigos_mochilas())
    else: 
        codigoi = request.args.get('codigo_KM','').strip()
        if codigoi == '':
            return render_template('EditarMochila.html', datos=None, usuarios=obtener_usuarios(), mochilas=obtener_codigos_mochilas())
        else:
            edi_KM = AltaMochilas()
            ok, valor= edi_KM.cargar_KM(codigoi)
            if not ok:
                flash(valor,'danger')
                return render_template('EditarMochila.html', datos=None, usuarios=obtener_usuarios(), mochilas=obtener_codigos_mochilas())
            else:
                return render_template('EditarMochila.html', datos=valor, usuarios=obtener_usuarios(), mochilas=obtener_codigos_mochilas())                    
@Inv.route('/buscar_herramienta', methods=['GET', 'POST'])
@login_required
@role_required(ROLES['Administrador'], ROLES['Almacen'])
def buscar_herramienta():
    """funcion que meramente sirve para renderizar la pagina del buscador"""
    return render_template('BuscadorHerramienta.html')
@Inv.route('/api/Buscar')
@login_required
@role_required(ROLES['Administrador'], ROLES['Almacen'])
def api_buscar():
    """Esta Funcion me permite ejecutar la busqueda parcial 
    por medio de los argumentos que obtiene constantemente"""
    termino = request.args.get('q','').strip()
    owner = request.args.get('owner','').strip()
    location = request.args.get('location','').strip()
    bus = BuscarH()
    ok, valor = bus.Buscarhe(termino, termino, owner, location)
    if not ok:
        flash(valor,'danger')
        return jsonify({'error': valor}), 500
    else:
        return jsonify(valor)
@Inv.route('/entra_sale', methods=['GET', 'POST'])
@login_required
@role_required(ROLES['Administrador'], ROLES['Almacen'], ROLES['Instalador'])
def entra_sale():
    """Esta funcion detecte el tipo de movimiento que se quiere realizar"""
    if request.method == 'POST':
        nombrea = request.form.get('nombrea', '').strip()
        nombrer = request.form.get('nombreR', '').strip()
        localidades = request.form.getlist('locala[]')
        herramientas = request.form.getlist('herra[]')
        acciones = request.form.getlist('acciona[]')
        observaciones = request.form.getlist('observacionesa[]')
        if es_instalador():
            nombrer = session.get('nombre', '')
        #El bloque anterior me sirve para obtener las listas con getlist
        # ya que permite obtener varias herramientas
        mov = Movimientos()#creo mi variable para comunicarme con la funcion
        for i, herramienta in enumerate(herramientas):
            #recorremos las herramientas con un for ya que son listas y
            # esto me permite realizar todas las inserciones
            locala = localidades[i].strip()
            cherra = herramientas[i].strip()
            acciona = acciones[i].strip()#limpiamos los campos para evitar espacios vacios
            obsa = observaciones[i].strip()

            if es_instalador() and acciona != "salida":
                flash(f"{cherra}: Como instalador solo puedes registrar préstamos, no devoluciones ni desasignaciones", 'danger')
                continue

            if not cherra:
                # Evita procesar herramientas vacías,
                # cada iteracion del for me permite obtener la herramienta depende la vuelta i
                continue

            # Verificar si la herramienta está dentro de una mochila
            moviMochi = MovimientosMochilas()
            ok_check, en_mochila = moviMochi.herramientaEnMochila(cherra)
            
            if en_mochila:
                flash(f"{cherra}: Esta herramienta está dentro de una mochila y no puede ser prestada individualmente", 'danger')
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
        return render_template('EntradaSalida.html', usuarios=obtener_usuarios(), herramientas=obtener_codigos_herramientas())
    else:
        return render_template('EntradaSalida.html', usuarios=obtener_usuarios(), herramientas=obtener_codigos_herramientas())    

@Inv.route('/prestamo_mochila', methods=['GET', 'POST'])
@login_required
@role_required(ROLES['Administrador'], ROLES['Almacen'], ROLES['Instalador'])
def prestamo_mochila():
    """Registra el préstamo de una mochila completa."""
    if request.method == 'POST':
        codigo_mochila = request.form.get('codigo_mochila', '').strip()
        responsable = request.form.get('responsable', '').strip()
        localidad = request.form.get('localidad', '').strip()

        if es_instalador():
            responsable = session.get('nombre', '')

        if not all([codigo_mochila, responsable, localidad]):
            flash('Debes capturar código, responsable y ubicación', 'danger')
            return render_template('PrestamoMochila.html', usuarios=obtener_usuarios(), mochilas=obtener_codigos_mochilas())

        ok, mensaje = prestar_mochila_completa(codigo_mochila, responsable, localidad)
        flash(mensaje, 'success' if ok else 'danger')

    return render_template('PrestamoMochila.html', usuarios=obtener_usuarios(), mochilas=obtener_codigos_mochilas())

@Inv.route('/llenarMochila', methods=['GET', 'POST'])
@login_required
@role_required(ROLES['Administrador'], ROLES['Almacen'])
def llenarMochila():

    if request.method == 'POST':

        nombre = request.form.get('nombreR', '').strip()
        codigoKM = request.form.getlist('codigoKM[]')
        codigoHERRA = request.form.getlist('codigoHERRA[]')
        accion = request.form.getlist('accion[]')

        moviMochi = MovimientosMochilas()

        for codigoKMs, codigoHERRAs, accions in zip(codigoKM, codigoHERRA, accion):

            codigoKMs = codigoKMs.strip()
            codigoHERRAs = codigoHERRAs.strip()

            if not codigoHERRAs:
                continue

            ok, estado_actual = moviMochi.estatusMoviMoch(codigoHERRAs)

            if not ok:
                estatus_invalidos = ['en_reparacion', 'extraviada', 'obsoleta']

                if estado_actual in estatus_invalidos:
                    flash(f"El estatus es: {estado_actual}", 'danger')
                    return render_template('LlenarMochila.html', usuarios=obtener_usuarios(), herramientas=obtener_codigos_herramientas(), mochilas=obtener_codigos_mochilas())

            ok, mensaje = moviMochi.moviMoch(nombre, codigoKMs, codigoHERRAs, accions)

            if not ok:
                flash(f"{codigoHERRAs}: {mensaje}", 'danger')
                return render_template('LlenarMochila.html', usuarios=obtener_usuarios(), herramientas=obtener_codigos_herramientas(), mochilas=obtener_codigos_mochilas())

            flash(f"{codigoHERRAs}: {mensaje}", 'success')

    return render_template('LlenarMochila.html', usuarios=obtener_usuarios(), herramientas=obtener_codigos_herramientas(), mochilas=obtener_codigos_mochilas())   
@Inv.route('/historial', methods=['GET','POST'])
@login_required
@role_required(ROLES['Administrador'], ROLES['Almacen'])
def historial():
    """este metodo me permite obtener el historial y compartirlo a la vista html"""
    filtros = {  # inicializamos siempre
        "nombrer": "",
        "herra": "",
        "propietario": "",
        "accion": "",
        "fechaini": "",
        "fechafin": ""
    }
    if request.method=='POST':
        filtros = {
            "nombrer" : request.form.get('nombreR','').strip(),
            "herra" : request.form.get('herra','').strip(),
            "propietario" : request.form.get('propietario','').strip(),
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
        if filtros["propietario"]:
            condicion.append("(person LIKE %s OR t.location LIKE %s OR m.observations LIKE %s)")
            propietario_like = f"%{filtros['propietario']}%"
            valor.extend([propietario_like, propietario_like, propietario_like])
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
            return render_template('Historial.html',filtros=filtros, usuarios=obtener_usuarios())
        else:
            return render_template('Historial.html', datos=valores, filtros=filtros, usuarios=obtener_usuarios())
    else:
        return render_template('Historial.html', filtros=filtros, usuarios=obtener_usuarios())
@Inv.route('/reporte', methods=['GET','POST'])
@login_required
@role_required(ROLES['Administrador'], ROLES['Almacen'])
def reporte():
    nombrer = request.form.get('nombreR','').strip()
    herra = request.form.get('herra','').strip()
    propietario = request.form.get('propietario','').strip()
    accion = request.form.get('accion','').strip()
    fechaini = request.form.get('fechaini','').strip()
    fechafin = request.form.get('fechafin','').strip()

    if not (nombrer or herra or propietario or accion or fechaini or fechafin):
        flash("Debes ingresar al menos un parametro", 'warning')
        return render_template('Historial.html', filtros=[])

    valor = []
    condicion= []

    if nombrer:
        condicion.append("person = %s")
        valor.append(nombrer)
    if propietario:
        condicion.append("(person LIKE %s OR t.location LIKE %s OR m.observations LIKE %s)")
        propietario_like = f"%{propietario}%"
        valor.extend([propietario_like, propietario_like, propietario_like])
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
        fecha_actual = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        # Renderizar HTML para PDF
        html = render_template("ReporteHistorial.html", datos=valores, fecha_actual=fecha_actual)

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
@Inv.route('/inventario', methods=['GET','POST'])
@login_required
@role_required(ROLES['Administrador'], ROLES['Almacen'])
def inventario():
    if request.method == 'POST':
        inventar = Inventario()
        ok, valores = inventar.inv()
        if ok:
            fecha_actual = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            # Renderizar HTML para PDF
            html = render_template("ReporteInventario.html", datos=valores, fecha_actual=fecha_actual)

            # Ruta absoluta a la carpeta src
            base_dirs = os.path.abspath(os.path.join(os.path.dirname(__file__)))

            # CSS absoluto
            css_path = os.path.join(base_dirs, "static", "css", "styleInventario.css")

            # PDF con base_url = carpeta src
            pdf = HTML(string=html, base_url=base_dirs).write_pdf(
                stylesheets=[CSS(css_path)]
                )

            response = make_response(pdf)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'inline; filename=reporteInventario.pdf'
            return response
        else:
            flash(valores, 'Danger')
            return render_template("Inventario.html")
    else:
        return render_template("Inventario.html")

@Inv.route('/mi_inventario', methods=['GET'])
@login_required
@role_required(ROLES['Instalador'])
def mi_inventario():
    """Muestra únicamente el inventario asignado al instalador en sesión."""
    ok, resultado = obtener_mi_inventario(session.get('nombre', ''))
    if not ok:
        flash(resultado, 'danger')
        resultado = {"herramientas": [], "mochilas": []}
    return render_template('MiInventario.html', inventario=resultado)

@Inv.route('/asignaciones_permanentes', methods=['GET'])
@login_required
@role_required(ROLES['Administrador'], ROLES['Almacen'])
def asignaciones_permanentes():
    """Muestra lista de asignaciones permanentes"""
    asig_perm = AsignacionesPermanentes()
    ok, asignaciones = asig_perm.listar_asignaciones_permanentes()
    
    if not ok:
        flash('Error al obtener asignaciones permanentes', 'danger')
        asignaciones = []
    
    return render_template('AsignacionesPermanentes.html', asignaciones=asignaciones)

@Inv.route('/marcar_permanente', methods=['POST'])
@login_required
@role_required(ROLES['Administrador'], ROLES['Almacen'])
def marcar_permanente():
    """Marca una herramienta como asignación permanente"""
    codigo_herramienta = request.form.get('codigo_herramienta', '').strip()
    responsable = request.form.get('responsable', '').strip()
    tipo_asignacion = request.form.get('tipo_asignacion', '').strip()
    
    if not all([codigo_herramienta, responsable, tipo_asignacion]):
        return jsonify({'success': False, 'message': 'Datos incompletos'}), 400
    
    asig_perm = AsignacionesPermanentes()
    user_name = session.get('nombre', '')
    ok, mensaje = asig_perm.marcar_asignacion_permanente(
        codigo_herramienta, responsable, tipo_asignacion, user_name
    )
    
    return jsonify({'success': ok, 'message': mensaje})

@Inv.route('/desmarcar_permanente', methods=['POST'])
@login_required
@role_required(ROLES['Administrador'])
def desmarcar_permanente():
    """Desmarca una asignación permanente"""
    codigo_herramienta = request.form.get('codigo_herramienta', '').strip()
    
    if not codigo_herramienta:
        return jsonify({'success': False, 'message': 'Código de herramienta requerido'}), 400
    
    asig_perm = AsignacionesPermanentes()
    user_name = session.get('nombre', '')
    ok, mensaje = asig_perm.desmarcar_asignacion_permanente(codigo_herramienta, user_name)
    
    return jsonify({'success': ok, 'message': mensaje})

@Inv.route('/verificar_asignacion_permanente', methods=['GET'])
@login_required
def verificar_asignacion_permanente():
    """Verifica si una herramienta tiene asignación permanente"""
    codigo_herramienta = request.args.get('codigo', '').strip()
    
    if not codigo_herramienta:
        return jsonify({'success': False, 'has_permanent': False}), 400
    
    asig_perm = AsignacionesPermanentes()
    ok, tiene_permanente = asig_perm.validar_asignacion_permanente(codigo_herramienta)
    
    if ok:
        ok_info, info = asig_perm.obtener_asignacion_permanente(codigo_herramienta)
        if ok_info:
            return jsonify({
                'success': True,
                'has_permanent': True,
                'assignment_type': info.get('assignment_type'),
                'assigned_to': info.get('user_name') or info.get('mochila_name') or info.get('responsable_name'),
                'assigned_at': str(info.get('assigned_at')),
                'assigned_by': info.get('assigned_by_name')
            })
    
    return jsonify({'success': True, 'has_permanent': False})

@Inv.route('/logout')
def logout():
    """Funcion para cerrar la sesion activa"""
    session.clear()
    return redirect(url_for('login'))
if __name__=='__main__':
    Inv.config.from_object(Config['development'])
    Inv.run(host='0.0.0.0', port=5000, debug=True)
