"""Uso esta clase para consultar las herramientas"""
import dataclasses
from DataBase.Conexion import Conexion, Error
@dataclasses.dataclass
class Inventario:
    """La clase que se encarga de consultar las herramientas registradas"""
    def inv(self)-> tuple[bool, list]:
        """Uso la funcion para consultar la base de datos"""
        db = Conexion()
        ok, Conn = db.conectar()
        if not ok:
            return False, Conn
        else:
            sql="SELECT * FROM tools WHERE status <> 'eliminada'"
            cursor = Conn.cursor(dictionary=True)
            try:#evaluo si puedo ejecutar la sentencia
                cursor.execute(sql)#esto lo uso para evitar la inyeccion de codigo
                resultados = cursor.fetchall()
                return True, resultados
            except Error as e:
                return False, str(e)
            finally:#se ejecute o no cierro el cursor y la conexion a la base de datos
                cursor.close()
                Conn.close()
        