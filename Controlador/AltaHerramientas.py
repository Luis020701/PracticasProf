"""Esta clase servira para dar de alta las herramientas"""
from datetime import datetime
import dataclasses
from DataBase.Conexion import Conexion , Error
@dataclasses.dataclass
class AltaHerramientas :
    """Clase para dar de alta herramientas en la base de datos"""
    def altah(self,nombre,tipo,brand,modelo,serie,codigoin,status,local,respon,precio,obs):
        """Funcion para dar de alta"""
        db = Conexion()
        ok, Conn = db.conectar()
        if not ok:
            return False, Conn
        else:
            cur=Conn.cursor()
            sql = "INSERT INTO tools (name, brand, model, serial_number, internal_code, tool_type, status, location, responsible, price, created_at, observations) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            datos =(
                nombre,
                brand,
                modelo,
                serie,
                codigoin,
                tipo,
                status,
                local,
                respon,
                precio,
                datetime.now(),
                obs
            )
            
            try:
                cur.execute(sql,datos)
                return True, "correcto"
            except Error as e:
                Conn.rollback()#Revierto los cambios si hay error
                return False, e
            finally:
                cur.close()
    
    def eliminarh(self, codigoinh):
        """Recibo la el codigo interno para poder eliminar  la herramienta"""
        db = Conexion()
        ok, Conn = db.conectar()
        if not ok:
            return False, Conn
        else:
            cur = Conn.cursor()
            sql = "DELETE FROM tools WHERE internal_code = %s"
            try:
                cur.execute(sql,(codigoinh,))
                if cur.rowcount == 0:#Verifico si encontro el registro
                    return False, "Herramienta no encontrada"
                else: 
                    Conn.commit()
                    return True, "Correcto"
            except Error as e:
                Conn.rollback()#Revierto los cambios
                return False, e
            finally:
                cur.close()
            