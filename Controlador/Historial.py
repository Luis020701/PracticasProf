"""Importo la Clase Conexion para poder trabajar con la Base de datos"""
import dataclasses
from DataBase.Conexion import Conexion, Error
@dataclasses.dataclass
class Historial:
    """la clase historial la uso para implementar las funciones 
    requeridas ppara las busqueda de estos datos"""
    def histo(self, herra, condi, valor):
        """Consulta la tabla de movimientos y devuelve resultados con joins a tools"""
        db = Conexion()
        ok, con = db.conectar()
        if not ok:
            return False, con

        try:
            cur = con.cursor(dictionary=True)
            cur1 = con.cursor(dictionary=True)

            sql1 = """
                SELECT m.*, t.name, t.internal_code, t.status
                FROM movements m
                JOIN tools t ON m.tool_id = t.id
            """

            # Hacemos copias de condiciones y valores para no modificar los originales
            condi_local = list(condi) if condi else []
            valor_local = list(valor) if valor else []

            if herra:
                # Buscar ID de la herramienta a partir del internal_code
                sql = "SELECT id FROM tools WHERE internal_code = %s"
                cur.execute(sql, (herra,))
                res = cur.fetchone()
                if not res:
                    return False, "Herramienta no encontrada"

                h = res["id"]
                condi_local.append("tool_id = %s")
                valor_local.append(h)

            if condi_local:
                sql1 += " WHERE " + " AND ".join(condi_local)

            cur1.execute(sql1, valor_local)
            resultados = cur1.fetchall()

            if not resultados:
                return False, "No se encontraron coincidencias"

            return True, resultados

        except Error as e:
            return False, str(e)
        finally:
            cur.close()
            cur1.close()
            con.close()

   