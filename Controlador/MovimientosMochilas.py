"""Importo la Clase Conexion para poder trabajar con la Base de datos"""
from datetime import datetime
import dataclasses
from threading import local
from DataBase.Conexion import Conexion, Error
@dataclasses.dataclass
class MovimientosMochilas:
    """la clase movientos me permite implementar funciones para realizar los moviemientos deseados"""
    def moviMoch(self,nombre,CodigoKM,CodigoHerra,accion) -> tuple[bool, list]:

        db = Conexion()
        ok, Conn = db.conectar()

        if not ok:
            return False, Conn

        try:

            cur = Conn.cursor()

            # Validar que accion sea "1" (agregar) o "0" (remover)
            if accion not in ["1", "0", 1, 0]:
                return False, "Acción inválida. Debe ser 1 (agregar) o 0 (remover)"

            # Convertir a string para consistencia
            accion = str(accion)

            # buscar herramienta y actualizar su estatus a prestamo en su propia tabla, debido a que ira dentro de la mochila
            sql="SELECT id FROM tools WHERE internal_code = %s AND status <> 'eliminada'"
            cur.execute(sql,(CodigoHerra,))
            res = cur.fetchone()

            if res is None:
                return False, "No se encontro la herramienta"
            idH = res[0]
            
            # Validación diferente según si es agregar o remover
            if accion == "1":  # Agregar a mochila
                # Verificar que la herramienta esté disponible (última acción debe ser "entrada")
                sqltool="Select action FROM movements WHERE tool_id = %s ORDER BY timestamp DESC LIMIT 1"
                cur.execute(sqltool,(idH,))
                res_action=cur.fetchone()
                
                if res_action is None:
                    return False, "La herramienta no tiene registro de movimientos. No se puede agregar a la mochila"
                
                if res_action[0] != "entrada":
                    # Si la última acción no es entrada, significa que está prestada (salida)
                    return False, "La herramienta está prestada y no puede ser agregada a la mochila. Debe devolverse primero al almacén"            
            # buscar mochila
            sql1="SELECT id_mochila FROM mochilas WHERE internal_code = %s"
            cur.execute(sql1,(CodigoKM,))
            res1 = cur.fetchone()

            if res1 is None:
                return False, "No se encontro la mochila"

            idKM = res1[0]

            # buscar usuario
            sql_user="SELECT id FROM user WHERE full_name = %s"
            cur.execute(sql_user,(nombre,))
            res_user = cur.fetchone()

            if res_user is None:
                return False, "No se encontro el usuario"

            idUs = res_user[0]
            sql_check = """
            SELECT inside
            FROM mochila_tools
            WHERE id_mochila = %s AND id_tool = %s
            """

            cur.execute(sql_check,(idKM,idH))
            estado = cur.fetchone()

            if accion == "1":
                # Agregar: No se puede añadir si ya está en cualquier mochila activa
                sql_any = "SELECT id_mochila FROM mochila_tools WHERE id_tool = %s AND inside = 1"
                cur.execute(sql_any,(idH,))
                existe_en_mochila = cur.fetchone()
                if existe_en_mochila is not None:
                    return False, "La herramienta ya está dentro de una mochila"
            else:
                # Remover: Solo se puede retirar si ya está dentro de esta mochila
                if estado is None or estado[0] != 1:
                    return False, "La herramienta no está dentro de esta mochila"

            #Actualizo el estatus de la herramienta en la tabla movements para llevar un control de su disponibilidad
            sql_mov= "INSERT INTO movements(tool_id,user_id,action,person,location,observations,timestamp) VALUES(%s,%s,%s,%s,%s,%s,%s)"
            
            if accion == "1":
                # Agregar a mochila
                action = 'salida'
                observacion = 'Añadida a mochila desde el sistema de prestamo de mochilas'
            else:
                # Remover de mochila
                action = 'entrada'
                observacion = 'Retirada de mochila para préstamo individual'
            
            datos=(
                    idH,
                    idUs,
                    action,
                    nombre,
                    'Mochila',
                    observacion,
                    datetime.now()
                      )
            cur.execute(sql_mov,datos)
            # insertar movimiento
            sql3 = """
            INSERT INTO mochila_tools
            (id_mochila,id_tool,inside,assigned_at,agregado_por)
            VALUES(%s,%s,%s,%s,%s)

            ON DUPLICATE KEY UPDATE
            inside = VALUES(inside),
            assigned_at = VALUES(assigned_at),
            agregado_por = VALUES(agregado_por)
            """

            datos = (
                idKM,
                idH,
                int(accion),
                datetime.now(),
                idUs
            )

            cur.execute(sql3,datos)
            Conn.commit()

            if accion == "1":
                return True, "Herramienta añadida a la mochila con éxito"
            else:
                return True, "Herramienta retirada de la mochila con éxito"

        except Error as e:

            Conn.rollback()
            return False, str(e)

        finally:

            cur.close()
            Conn.close()
    
    def estatusMoviMoch(self,CodigoHerra) -> tuple[bool, list]:
        """Lo que checa esta funcion es el estatus de las herramientas para futuras validaciones"""
        db = Conexion()
        ok, Conn = db.conectar()
        if not ok:
            return False, Conn
        else:
            try:
                cur=Conn.cursor()
                cur1=Conn.cursor()
                sql="SELECT id, status FROM tools WHERE internal_code = %s AND status <> 'eliminada'"#obtengo el id de la herramienta para poder filtrar los al igual que su status para evaluarlo
                cur.execute(sql,(CodigoHerra,))
                res=cur.fetchone()
                if res is  None:
                    return False, 'No se encontro el id de la herramienta'
                idh, sts= res
                estatus_invalidos = ['en_reparacion', 'extraviada', 'obsoleta']
                if sts in estatus_invalidos:#valido que estatus tiene
                    return False, sts#si tiene alguno de estos 3 manda error
                sql1="SELECT inside FROM mochila_tools WHERE id_tool = %s AND inside = 1"#consulto si la herramienta esta dentro de una mochila
                cur1.execute(sql1,(idh,))
                res1=cur1.fetchone()
                if res1 is None:
                    return True,'La herramienta no está en ninguna mochila'#si no esta regreso verdadero (disponible)
                else:
                    return False, "La herramienta está dentro de una mochila"#si esta regreso falso (no disponible)
            except Error as e:
                return False, str(e)
            finally:
                cur.close()
                cur1.close()
                Conn.close()
    
    def herramientaEnMochila(self, CodigoHerra) -> tuple[bool, bool]:
        """Verifica si una herramienta está dentro de una mochila (inside=1)
        
        Retorna:
            (ok, en_mochila): 
                - ok=False si hay error
                - en_mochila=True si la herramienta está dentro de una mochila
                - en_mochila=False si la herramienta no está en ninguna mochila
        """
        db = Conexion()
        ok, Conn = db.conectar()
        if not ok:
            return False, False
        else:
            try:
                cur = Conn.cursor()
                # Buscar el id de la herramienta
                sql = "SELECT id FROM tools WHERE internal_code = %s AND status <> 'eliminada'"
                cur.execute(sql, (CodigoHerra,))
                res = cur.fetchone()
                
                if res is None:
                    return False, False
                
                idh = res[0]
                
                # Verificar si existe en mochila_tools con inside=1
                sql_check = "SELECT inside FROM mochila_tools WHERE id_tool = %s AND inside = 1"
                cur.execute(sql_check, (idh,))
                res_check = cur.fetchone()
                
                if res_check is not None:
                    return True, True  # La herramienta está dentro de una mochila
                else:
                    return True, False  # La herramienta no está en ninguna mochila
                    
            except Error as e:
                return False, False
            finally:
                cur.close()
                Conn.close()