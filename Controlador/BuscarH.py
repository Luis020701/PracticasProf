"""Esta clase servira para buscar las herramientas"""
import dataclasses
from DataBase.Conexion import Conexion , Error
@dataclasses.dataclass
class BuscarH:
    """Clase para la busqueda de herramientas"""
    def Buscarhe(self, name, codigoh, owner=None, location=None) -> tuple[bool, list]:
        """ La funcion sirve para buscar de manera dinamica la herramienta y mostrar en que mochila esta"""
        db = Conexion()
        ok, Conn = db.conectar()
        if not ok:
            return False, Conn
        else:
            # JOIN con mochila_tools y mochilas para obtener el nombre de la mochila si la herramienta está dentro
            # y con el último movimiento para calcular propietario actual
            sql = """
            SELECT 
                t.*, 
                m.nombre AS mochila_nombre,
                mt.inside AS en_mochila,
                lm.last_person,
                lm.last_action,
                pa.assignment_type AS permanent_assignment_type,
                pa.responsable_name,
                u.full_name AS permanent_user,
                pm.nombre AS permanent_mochila,
                CASE
                    WHEN pa.id IS NOT NULL AND pa.assignment_type = 'user' THEN CONCAT('Permanente: ', COALESCE(u.full_name, pa.responsable_name))
                    WHEN pa.id IS NOT NULL AND pa.assignment_type = 'mochila' THEN CONCAT('Permanente: ', pm.nombre)
                    WHEN mt.inside = 1 THEN CONCAT('Mochila: ', m.nombre)
                    WHEN lm.last_action = 'salida' THEN lm.last_person
                    ELSE t.responsible
                END AS current_owner,
                CASE
                    WHEN pa.id IS NOT NULL THEN 'permanente'
                    ELSE 'temporal'
                END AS assignment_status
            FROM tools t
            LEFT JOIN permanent_assignments pa ON pa.tool_id = t.id AND pa.active = 1
            LEFT JOIN user u ON pa.user_id = u.id
            LEFT JOIN mochilas pm ON pa.mochila_id = pm.id_mochila
            LEFT JOIN mochila_tools mt ON t.id = mt.id_tool AND mt.inside = 1
            LEFT JOIN mochilas m ON mt.id_mochila = m.id_mochila
            LEFT JOIN (
                SELECT sub.tool_id, sub.person AS last_person, sub.action AS last_action
                FROM movements sub
                JOIN (
                    SELECT tool_id, MAX(timestamp) AS max_ts
                    FROM movements
                    GROUP BY tool_id
                ) latest ON sub.tool_id = latest.tool_id AND sub.timestamp = latest.max_ts
            ) lm ON lm.tool_id = t.id
            WHERE t.status <> 'eliminada'
            """
            if not name and not owner and not location:
                return True, []

            params = []
            if name:
                sql += " AND (t.name LIKE %s OR t.internal_code LIKE %s)"
                params.extend([f"%{name}%", f"%{codigoh}%"])
            if owner:
                sql += " AND (t.responsible LIKE %s OR m.nombre LIKE %s OR lm.last_person LIKE %s OR u.full_name LIKE %s OR pm.nombre LIKE %s)"
                like_owner = f"%{owner}%"
                params.extend([like_owner, like_owner, like_owner, like_owner, like_owner])
            if location:
                sql += " AND t.location LIKE %s"
                params.append(f"%{location}%")

            cur = Conn.cursor(dictionary=True)
            try:
                cur.execute(sql, tuple(params))
                resultado = cur.fetchall()
                return True, resultado
            except Error as e:
                return False, str(e)
            finally:
                cur.close()
                Conn.close()