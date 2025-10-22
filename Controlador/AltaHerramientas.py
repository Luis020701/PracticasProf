"""Esta clase servira para dar de alta las herramientas"""
from datetime import datetime
import dataclasses
from DataBase.Conexion import Conexion , Error
@dataclasses.dataclass
class AltaHerramientas :
    """Clase para dar de alta herramientas en la base de datos"""
    def altah(self,nombre,tipo,brand,modelo,
              serie,codigoin,status,local,
              respon,precio,obs) -> tuple[bool, list]:
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
            
            try:#El try evalua la sentencia y ejecuta el codigo en caso de que funcione
                cur.execute(sql,datos)
                Conn.commit()
                return True, "correcto"
            except Error as e:#except regresa False para indicar el error e indica cual es el error con la variable e
                Conn.rollback()#Revierto los cambios si hay error
                return False, str(e)
            finally:#ejecuta si o si el cerrado del cursor para no dejarlo abierto
                cur.close()
                Conn.close()
    def eliminarh(self, codigoinh) -> tuple[bool, list]:
        """Recibo la el codigo interno para poder eliminar  la herramienta"""
        db = Conexion()
        ok, Conn = db.conectar()
        if not ok:
            return False, Conn
        else:
            cur = Conn.cursor()
            sql = "UPDATE tools SET status = 'eliminada' WHERE internal_code = %s"#hago solo un borrado logico
            try:#El try evalua la sentencia y ejecuta el codigo en caso de que funcione
                cur.execute(sql,(codigoinh,))
                if cur.rowcount == 0:#Verifico si encontro el registro
                    return False, "Herramienta no encontrada"
                else: 
                    Conn.commit()
                    return True, "Correcto"
            except Error as e:#except regresa False para indicar el error e indica cual es el error con la variable e
                Conn.rollback()#Revierto los cambios
                return False, str(e)
            finally:#ejecuta si o si el cerrado del cursor para no dejarlo abierto
                cur.close()
                Conn.close()               
    def editah(self,nombre,tipo,brand,modelo,
               serie,codigoin,status,local,
               respon,precio,obs) -> tuple[bool, list]:
        """Funcion para editar """
        db = Conexion()
        ok, Conn = db.conectar()
        if not ok:
            return False, Conn
        else:
            sql= "UPDATE TOOLS SET name=%s, brand=%s, model=%s, serial_number=%s, tool_type=%s, status=%s, location=%s, responsible=%s, price=%s, created_at=%s, observations=%s WHERE internal_code = %s AND status <> 'eliminada'"
            datos=(#Tupla para la sentencia parametrizada
                nombre,
                brand,
                modelo,
                serie,
                tipo,
                status,
                local,
                respon,
                precio,
                datetime.now(),#Indico la fecha y hora actual
                obs,
                codigoin
            )
            try:
                cur = Conn.cursor()
                cur.execute(sql,datos)
                Conn.commit()
                return True, 'Herramienta Actualizada'
            except Error as e:
                return False, str(e)
            finally:
                cur.close()
                Conn.close()
    def cargardatos(self,codigoinh) -> tuple[bool, list]:
        """Uso esta funcion para cargar los datos almacenados para posteriormente ser editados"""
        db = Conexion()
        ok, Conn = db.conectar()
        if not ok:
            return False, Conn
        else:
            cur = Conn.cursor(dictionary=True)
            sql = "SELECT * from tools WHERE internal_code = %s and status <> 'eliminada'"
            try:
                cur.execute(sql,(codigoinh,))
                resultado = cur.fetchone()
                if resultado is None:
                    return False,"Herramienta no encontrada"
                else:
                    return True, resultado
            except Error as e:
                return False, str(e)
            finally:
                cur.close()
                Conn.close()