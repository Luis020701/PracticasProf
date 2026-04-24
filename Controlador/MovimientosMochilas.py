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

            # buscar herramienta y actualizar su estatus a prestamo en su propia tabla, debido a que ira dentro de la mochila
            sql="SELECT id FROM tools WHERE internal_code = %s AND status <> 'eliminada'"
            cur.execute(sql,(CodigoHerra,))
            res = cur.fetchone()

            if res is None:
                return False, "No se encontro la herramienta"
            idH = res[0]
            sqltool="Select action FROM movements WHERE tool_id = %s ORDER BY timestamp DESC LIMIT 1"
            cur.execute(sqltool,(idH,))
            res2=cur.fetchone()
            if res2 is None or res2[0]=="salida":
                return False, "La herramienta no esta disponible para ser añadida a la mochila"               
            # buscar mochila
            sql1="SELECT id_mochila FROM mochilas WHERE internal_code = %s"
            cur.execute(sql1,(CodigoKM,))
            res1 = cur.fetchone()

            if res1 is None:
                return False, "No se encontro la mochila"

            idKM = res1[0]

            # buscar usuario
            sql2="SELECT id FROM user WHERE full_name = %s"
            cur.execute(sql2,(nombre,))
            res2 = cur.fetchone()

            if res2 is None:
                return False, "No se encontro el usuario"

            idUs = res2[0]
            sql_check = """
            SELECT inside
            FROM mochila_tools
            WHERE id_mochila = %s AND id_tool = %s
            """

            cur.execute(sql_check,(idKM,idH))
            estado = cur.fetchone()

            if estado:

                if estado[0] == 1 and accion == "1":
                    return False, "La herramienta ya está dentro de la mochila"

                if estado[0] == 0 and accion == "0":
                    return False, "La herramienta ya está fuera de la mochila"
            #Actualizo el estatus de la herremienta en la tabla movements para llevar un control de su disponibilidad
            sql2= "INSERT INTO movements(tool_id,user_id,action,person,location,observations,timestamp) VALUES(%s,%s,%s,%s,%s,%s,%s)"
            datos=(
                    idH,
                    idUs,
                    'salida',
                    nombre,
                    'Mochila',
                    'Añadida a mochila desde el sistema de prestamo de mochilas',
                    datetime.now()
                      )
            cur.execute(sql2,datos)
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
                return True, "Añadida con exito"
            else:
                return True, "Eliminada con exito"

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
                sql1="SELECT id_tool FROM mochila_tools WHERE id_tool = %s"#consulto si la herramienta esta en alguna mochila
                cur1.execute(sql1,(idh,))
                res1=cur1.fetchone()
                if res1 is None:
                    return False,'No se encontro registro de la herramienta en la mochila'#si no esta regreso falso
                else:
                    return True, "La herramienta esta en la mochila"#si esta regreso verdadero
            except Error as e:
                return False, str(e)
            finally:
                cur.close()
                cur1.close()
                Conn.close()