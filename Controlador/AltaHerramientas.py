"""Esta clase servira para dar de alta las herramientas"""
from datetime import datetime
import dataclasses
from DataBase.Conexion import Conexion
@dataclasses.dataclass
class AltaHerramientas :
    """Clase para dar de alta herramientas en la base de datos"""
    def altah(self,nombre,tipo,brand,modelo,serie,codigoin,status,local,respon,precio,obs):
        """Funcion para dar de alta"""
        db = Conexion()
        Conn = db.conectar()
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
            cur.execute(sql,datos)
            Conn.commit()
            cur=Conn.cursor()
            cur.close()
            return True