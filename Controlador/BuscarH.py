"""Esta clase servira para buscar las herramientas"""
import dataclasses
from DataBase.Conexion import Conexion , Error
@dataclasses.dataclass
class BuscarH:
    """Clase para la busqueda de herramientas"""
    def Buscarhe(self, name, codigoh) -> tuple[bool, list]:
        """ La funcion sirve para buscar de manera dinamica la herramienta"""
        db = Conexion()
        ok, Conn = db.conectar()
        if not ok:
            return False, Conn
        else:
            sql="SELECT * FROM tools WHERE (name LIKE %s or internal_code LIKE %s) AND status <> 'eliminada'"
            cur = Conn.cursor(dictionary=True)
            try:
                name = f"%{name}%"#añado comodines para poder hacer busquedas parciales que contengan el valor que estoy recibiendo
                codigoh= f"%{codigoh}%"#añado comodines para poder hacer busquedas parciales
                cur.execute(sql,(name, codigoh))
                resultado=cur.fetchall()
                return True, resultado
            except Error as e:
                return False, str(e)
            finally:
                cur.close()
                Conn.close()