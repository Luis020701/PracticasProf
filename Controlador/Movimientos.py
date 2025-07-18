"""Importo la Clase Conexion para poder trabajar con la Base de datos"""
from datetime import datetime
import dataclasses
from werkzeug.security import generate_password_hash,check_password_hash
from DataBase.Conexion import Conexion, Error
@dataclasses.dataclass
class Movimientos:
    def mov(self,nombre,nombrer,local,accion,obs,herra):
        """Esta funcion me sirve para dar entrada o salida a la herramienta"""
        db = Conexion()
        ok, Conn = db.conectar()
        if not ok:
            return False, Conn
        else:
            try:
                cur = Conn.cursor()
                cur1=Conn.cursor()
                cur2=Conn.cursor()
                sql="SELECT id FROM tools WHERE internal_code = %s"#obtengo el id de la herramienta en base al nombre
                cur.execute(sql,(herra,))
                res=cur.fetchone()
                if res is not None:
                    idH=res[0]
                    sql1="SELECT id FROM user WHERE full_name = %s"#obtengo el id del usuario en base al nombre
                    cur1.execute(sql1,(nombre,))
                    res1=cur1.fetchone()
                    if res1 is not None:
                        idUs = res1[0]
                        sql2= "INSERT INTO movements(tool_id,user_id,action,person,location,observations,timestamp) VALUES(%s,%s,%s,%s,%s,%s,%s)"
                        datos=(
                            idH,
                            idUs,
                            accion,
                            nombrer,
                            local,
                            obs,
                            datetime.now()
                        )
                        cur2.execute(sql2,datos)
                        Conn.commit()
                        if accion=="entrada":
                            return True, "Devuelta con exito"
                        elif accion=="salida":
                            return True, "Prestamo exitoso"
                    else:
                        return False, 'No se encontro el usuario'
                else:
                    return False, 'No se encontro la herramienta'

            except Error as e:
                Conn.rollback()#Revierto los cambios si hay error
                return False, str(e)
            finally:
                cur.close()
                cur1.close()
                cur2.close()
                Conn.close()
    
    def estatusMov(self,herra):
        db = Conexion()
        ok, Conn = db.conectar()
        if not ok:
            return False, Conn
        else:
            try:
                cur=Conn.cursor()
                cur1=Conn.cursor()
                sql="SELECT id FROM tools WHERE internal_code = %s"#obtengo el id de la herramienta para poder filtrar los movimientos
                cur.execute(sql,(herra,))
                res=cur.fetchone()
                if res is  None:
                    return False, 'No se encontro el id de la herramienta'
                idh=res[0]
                sql1="SELECT action FROM movements WHERE tool_id = %s ORDER BY timestamp DESC LIMIT 1"#consulto la accion para poder evitar problemas de insercion
                cur1.execute(sql1,(idh,))
                res1=cur1.fetchone()
                if res1 is None:
                    return False,'No se encontro registro de la herramienta'
                acc=res1[0]
                return True, acc
            except Error as e:
                return False, str(e)
            finally:
                cur.close()
                cur1.close()
                Conn.close()