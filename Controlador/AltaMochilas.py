from datetime import datetime
import dataclasses
from DataBase.Conexion import Conexion , Error
@dataclasses.dataclass
class AltaMochilas:
    def registro_kit(self,nombre,respos,status,descripcion,codigoi):
        db = Conexion()
        ok, Conn = db.conectar()
        if not ok:
            return False, Conn
        else:
            cur = Conn.cursor()
            sql="INSERT INTO mochilas (internal_code, tipo, nombre, descripcion, estado, responsable) VALUES(%s,%s,%s,%s,%s,%s)"
            datos = (
                codigoi,
                "mochila",
                nombre,
                descripcion,
                status,
                respos
            )
            try:
                cur.execute(sql,datos)
                Conn.commit()
                return True, 'Creacion de Mochila/Kit correcta'
            except Error as e:
                Conn.rollback()#Revierto los cambios si hay error
                return False, str(e)
            finally:
                cur.close()
                Conn.close()
                
    def editar_KM(self,nombre,respos,status,descripcion,codigo):
        db = Conexion()
        ok, Conn = db.conectar()
        if not ok:  
            return False,Conn
        else:
            cur = Conn.cursor()
            sql = "UPDATE mochilas SET nombre = %s, descripcion = %s, estado = %s, responsable = %s WHERE internal_code = %s AND activo <> 0"
            datos = (
                nombre,
                descripcion,
                status,
                respos,
                codigo
            )
            try:
                cur.execute(sql,datos)
                if cur.rowcount == 0:
                    Conn.rollback()
                    return False, "No se encontró la mochila o está inactiva"
                Conn.commit()
                return True, 'Actualizacion Exitosa'
            except Error as e:
                Conn.rollback()
                return False, str(e)
            finally:
                cur.close()
                Conn.close()
                
    def cargar_KM(self, codigoi):
        """esta funcion busca y devuelve los datos de la mochila"""
        db = Conexion()
        ok, Conn = db.conectar()
        if not ok:
            return False, Conn
        else:
            cur = Conn.cursor(dictionary=True)
            sql = "SELECT * FROM MOCHILAS WHERE internal_code = %s"
            try:
                cur.execute(sql,(codigoi,))
                resultado = cur.fetchone()
                if resultado is None:
                    return False, "Sin datos!"
                else:
                    return True, resultado
            except Error as e:
                return False, str(e)
            finally:
                cur.close()
                Conn.close()
        