"""Esta clase servira para dar de alta las herramientas"""
from datetime import datetime
import dataclasses
from DataBase.Conexion import Conexion
@dataclasses.dataclass
class AltaHerramientas :
    """Clase para dar de alta herramientas en la base de datos"""
    Conn = Conexion.Con.cursor()
    def altah(self,nombre,tipo,brand,modelo,serie,codigoin,status,local,respon,precio,obs):
        """Funcion para dar de alta"""
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
        self.Conn.execute(sql,datos)
        Conexion.Con.commit()
        return True