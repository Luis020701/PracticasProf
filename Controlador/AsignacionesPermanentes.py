"""Controlador para gestionar asignaciones permanentes de herramientas"""
import dataclasses
from datetime import datetime
from DataBase.Conexion import Conexion, Error


@dataclasses.dataclass
class AsignacionesPermanentes:
    """Maneja las asignaciones permanentes de herramientas a usuarios o mochilas"""

    def marcar_asignacion_permanente(
        self, codigo_herramienta: str, responsable: str, tipo_asignacion: str = 'auto', usuario_admin: str = ''
    ) -> tuple[bool, str]:
        """
        Marca una herramienta como asignación permanente.
        
        Args:
            codigo_herramienta: Código interno de la herramienta
            responsable: Nombre de usuario o código de mochila responsable
            tipo_asignacion: 'user', 'mochila' o 'auto' para inferir automáticamente
            usuario_admin: Usuario que realiza la acción (debe ser admin o almacenista)
        
        Returns:
            (bool, str): (éxito, mensaje)
        """
        db = Conexion()
        ok, conn = db.conectar()
        if not ok:
            return False, conn

        try:
            cur = conn.cursor(dictionary=True)

            # Obtener ID de la herramienta
            sql = "SELECT id FROM tools WHERE internal_code = %s AND status <> 'eliminada'"
            cur.execute(sql, (codigo_herramienta,))
            res_tool = cur.fetchone()

            if not res_tool:
                return False, "Herramienta no encontrada"

            tool_id = res_tool["id"]

            # Obtener ID de usuario administrador
            sql_admin = "SELECT id FROM user WHERE full_name = %s"
            cur.execute(sql_admin, (usuario_admin,))
            res_admin = cur.fetchone()

            if not res_admin:
                return False, "Usuario administrador no encontrado"

            admin_id = res_admin["id"]

            user_id = None
            mochila_id = None

            # Inferir tipo de asignación si no se especifica explícitamente
            if tipo_asignacion == "auto":
                sql_resp = "SELECT id FROM user WHERE full_name = %s"
                cur.execute(sql_resp, (responsable,))
                res_resp = cur.fetchone()
                if res_resp:
                    user_id = res_resp["id"]
                    tipo_asignacion = "user"
                else:
                    sql_resp = "SELECT id_mochila FROM mochilas WHERE internal_code = %s"
                    cur.execute(sql_resp, (responsable,))
                    res_resp = cur.fetchone()
                    if res_resp:
                        mochila_id = res_resp["id_mochila"]
                        tipo_asignacion = "mochila"
                    else:
                        # Permitir nombres personalizados que no estén en BD
                        # Se asume que es una asignación a usuario si no se encuentra en mochilas
                        tipo_asignacion = "user"
                        user_id = None
            elif tipo_asignacion == "user":
                sql_resp = "SELECT id FROM user WHERE full_name = %s"
                cur.execute(sql_resp, (responsable,))
                res_resp = cur.fetchone()

                if res_resp:
                    user_id = res_resp["id"]
                else:
                    # Permitir nombres personalizados de usuarios que no estén en BD
                    user_id = None
            elif tipo_asignacion == "mochila":
                sql_resp = "SELECT id_mochila FROM mochilas WHERE internal_code = %s"
                cur.execute(sql_resp, (responsable,))
                res_resp = cur.fetchone()

                if not res_resp:
                    return False, "Mochila no encontrada"

                mochila_id = res_resp["id_mochila"]
            else:
                return False, "Tipo de asignación inválido"

            # Verificar si ya existe una asignación permanente
            sql_check = (
                "SELECT id FROM permanent_assignments WHERE tool_id = %s AND active = 1"
            )
            cur.execute(sql_check, (tool_id,))
            if cur.fetchone():
                return False, "La herramienta ya tiene una asignación permanente activa"

            # Insertar o actualizar asignación permanente
            sql_insert = """
                INSERT INTO permanent_assignments
                (tool_id, user_id, mochila_id, responsable_name, assignment_type, assigned_by, assigned_at, active)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), 1)
                ON DUPLICATE KEY UPDATE
                    user_id = VALUES(user_id),
                    mochila_id = VALUES(mochila_id),
                    responsable_name = VALUES(responsable_name),
                    active = 1,
                    assigned_by = VALUES(assigned_by),
                    assigned_at = NOW()
            """

            cur.execute(
                sql_insert, (tool_id, user_id, mochila_id, responsable, tipo_asignacion, admin_id)
            )
            conn.commit()

            return True, f"Asignación permanente marcada para {responsable}"

        except Error as e:
            conn.rollback()
            return False, str(e)
        finally:
            cur.close()
            conn.close()

    def desmarcar_asignacion_permanente(
        self, codigo_herramienta: str, usuario_admin: str
    ) -> tuple[bool, str]:
        """
        Desmarca una asignación permanente (solo administrador).
        
        Args:
            codigo_herramienta: Código interno de la herramienta
            usuario_admin: Usuario que realiza la acción
        
        Returns:
            (bool, str): (éxito, mensaje)
        """
        db = Conexion()
        ok, conn = db.conectar()
        if not ok:
            return False, conn

        try:
            cur = conn.cursor()

            # Obtener ID de la herramienta
            sql = "SELECT id FROM tools WHERE internal_code = %s AND status <> 'eliminada'"
            cur.execute(sql, (codigo_herramienta,))
            res_tool = cur.fetchone()

            if not res_tool:
                return False, "Herramienta no encontrada"

            tool_id = res_tool[0]

            # Desmarcar asignación permanente
            sql_update = (
                "UPDATE permanent_assignments SET active = 0 WHERE tool_id = %s"
            )
            cur.execute(sql_update, (tool_id,))

            if cur.rowcount == 0:
                return False, "No hay asignación permanente para desmarcar"

            conn.commit()
            return True, "Asignación permanente desmarcada"

        except Error as e:
            conn.rollback()
            return False, str(e)
        finally:
            cur.close()
            conn.close()

    def obtener_asignacion_permanente(
        self, codigo_herramienta: str
    ) -> tuple[bool, dict]:
        """
        Obtiene la información de asignación permanente de una herramienta.
        
        Args:
            codigo_herramienta: Código interno de la herramienta
        
        Returns:
            (bool, dict): (éxito, datos de asignación o mensaje de error)
        """
        db = Conexion()
        ok, conn = db.conectar()
        if not ok:
            return False, {"error": conn}

        try:
            cur = conn.cursor(dictionary=True)

            # Obtener ID de la herramienta
            sql = "SELECT id FROM tools WHERE internal_code = %s AND status <> 'eliminada'"
            cur.execute(sql, (codigo_herramienta,))
            res_tool = cur.fetchone()

            if not res_tool:
                return False, {"error": "Herramienta no encontrada"}

            tool_id = res_tool["id"]

            # Obtener asignación permanente
            sql_query = """
                SELECT 
                    pa.id,
                    pa.assignment_type,
                    pa.responsable_name,
                    u.full_name as user_name,
                    m.nombre as mochila_name,
                    pa.assigned_at,
                    admin.full_name as assigned_by_name
                FROM permanent_assignments pa
                LEFT JOIN user u ON pa.user_id = u.id
                LEFT JOIN mochilas m ON pa.mochila_id = m.id_mochila
                LEFT JOIN user admin ON pa.assigned_by = admin.id
                WHERE pa.tool_id = %s AND pa.active = 1
            """

            cur.execute(sql_query, (tool_id,))
            result = cur.fetchone()

            if not result:
                return False, {"error": "Sin asignación permanente"}

            return True, result

        except Error as e:
            return False, {"error": str(e)}
        finally:
            cur.close()
            conn.close()

    def validar_asignacion_permanente(self, codigo_herramienta: str) -> tuple[bool, bool]:
        """
        Verifica si una herramienta tiene asignación permanente activa.
        
        Args:
            codigo_herramienta: Código interno de la herramienta
        
        Returns:
            (bool, bool): (éxito, tiene_asignacion_permanente)
        """
        db = Conexion()
        ok, conn = db.conectar()
        if not ok:
            return False, False

        try:
            cur = conn.cursor()

            # Obtener ID de la herramienta
            sql = "SELECT id FROM tools WHERE internal_code = %s AND status <> 'eliminada'"
            cur.execute(sql, (codigo_herramienta,))
            res_tool = cur.fetchone()

            if not res_tool:
                return False, False

            tool_id = res_tool[0]

            # Verificar si existe asignación permanente activa
            sql_check = (
                "SELECT COUNT(*) FROM permanent_assignments WHERE tool_id = %s AND active = 1"
            )
            cur.execute(sql_check, (tool_id,))
            count = cur.fetchone()[0]

            return True, count > 0

        except Error as e:
            return False, False
        finally:
            cur.close()
            conn.close()

    def listar_asignaciones_permanentes(self) -> tuple[bool, list]:
        """
        Lista todas las asignaciones permanentes activas.
        
        Returns:
            (bool, list): (éxito, lista de asignaciones)
        """
        db = Conexion()
        ok, conn = db.conectar()
        if not ok:
            return False, []

        try:
            cur = conn.cursor(dictionary=True)

            sql_query = """
                SELECT 
                    t.internal_code,
                    t.name as tool_name,
                    pa.assignment_type,
                    pa.responsable_name,
                    u.full_name as user_name,
                    m.nombre as mochila_name,
                    pa.assigned_at,
                    admin.full_name as assigned_by_name
                FROM permanent_assignments pa
                JOIN tools t ON pa.tool_id = t.id
                LEFT JOIN user u ON pa.user_id = u.id
                LEFT JOIN mochilas m ON pa.mochila_id = m.id_mochila
                LEFT JOIN user admin ON pa.assigned_by = admin.id
                WHERE pa.active = 1
                ORDER BY t.internal_code
            """

            cur.execute(sql_query)
            resultados = cur.fetchall()

            return True, resultados

        except Error as e:
            return False, []
        finally:
            cur.close()
            conn.close()
