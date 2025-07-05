"""Esta clase servira para buscar las herramientas"""
from datetime import datetime
import dataclasses
from DataBase.Conexion import Conexion , Error
@dataclasses.dataclass
class BuscarH:
    def Buscarhe(self, name, codigoh):
        db = Conexion()
        ok, Conn = db.conectar()
        if not ok:
            return False, Conn
        else:
            sql="SELECT * FROM tools WHERE name LIKE %s or internal_code LIKE %s"
            cur = Conn.cursor(dictionary=True)
            try:
                name = f"%{name}%"
                codigoh= f"%{codigoh}%"
                cur.execute(sql,(name, codigoh))
                resultado=cur.fetchall()
                return True, resultado
            except Error as e:
                return False, str(e)
            finally:
                cur.close()
                Conn.close()