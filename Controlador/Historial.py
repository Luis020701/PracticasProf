"""Importo la Clase Conexion para poder trabajar con la Base de datos"""
import dataclasses
from DataBase.Conexion import Conexion, Error
@dataclasses.dataclass
class Historial:
    """la clase historial la uso para implementar las funciones requeridas ppara las busqueda de estos datos"""
    def histo(self,herra,condi,valor):
        """esta funcion la uso para hacer la consulta de la tabla de movimientos"""
        db = Conexion()
        ok,con = db.conectar()
        if not ok:
            return False,con
        else:
            try:
                cur = con.cursor()
                cur1 = con.cursor()
                sql1="SELECT * from movements"
                if not herra:
                    if condi:
                        sql1 += " WHERE " + " AND ".join(condi)
                        cur1.execute(sql1,valor)
                        resultados = cur1.fetchall()
                        return True, resultados
                else:
                    sql="SELECT id FROM tools WHERE internal_code = %s"
                    cur.execute(sql,(herra,))
                    res =cur.fetchone()
                    if not res:
                        return False, "Herramienta no encontrada"
                    h=res[0] 
                    condi.append("tool_id = %s")
                    valor.append(h)
                    if condi:
                        sql1 += " WHERE " + " AND ".join(condi)
                        cur1.execute(sql1,valor)
                        resultados = cur1.fetchall()
                        if not resultados:
                            return False, "No se encontraron coincidencias"
                        else:
                            return True, resultados
            except Error as e:
                return False, str(e)
            finally:
                cur.close()
                cur1.close()
                con.close()
   