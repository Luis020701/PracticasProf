"""Importo la Clase Conexion para poder trabajar con la Base de datos"""
from datetime import datetime
import dataclasses
from DataBase.Conexion import Conexion, Error
@dataclasses.dataclass
class Movimientos:
    """la clase movientos me permite implementar funciones para realizar los moviemientos deseados"""
    def mov(self, nombre, nombrer, local, accion, obs, herra, rol=None) -> tuple[bool, list]:
        """Esta funcion me sirve para dar entrada o salida a la herramienta
        
        Args:
            rol: Rol del usuario (1=Administrador, 2=Almacenista, 3=Instalador). Requerido para cambios de propietario.
        """
        db = Conexion()
        ok, Conn = db.conectar()
        if not ok:
            return False, Conn
        else:
            try:
                cur = Conn.cursor()
                cur1 = Conn.cursor()
                cur2 = Conn.cursor()
                cur3 = Conn.cursor()
                
                sql = "SELECT id FROM tools WHERE internal_code = %s AND status <> 'eliminada'"
                cur.execute(sql, (herra,))
                res = cur.fetchone()
                if res is not None:
                    idH = res[0]
                    
                    # Validar asignación permanente si el cambio es de propietario
                    if accion == "cambio de propietario":
                        sql_check_permanent = """
                            SELECT pa.id, COALESCE(u.full_name, pa.responsable_name), m.nombre 
                            FROM permanent_assignments pa
                            LEFT JOIN user u ON pa.user_id = u.id
                            LEFT JOIN mochilas m ON pa.mochila_id = m.id_mochila
                            WHERE pa.tool_id = %s AND pa.active = 1
                        """
                        cur3.execute(sql_check_permanent, (idH,))
                        res_perm = cur3.fetchone()
                        
                        if res_perm is not None:
                            # Verificar permisos para cambiar asignación permanente
                            allowed_roles = [1, 2]  # 1=Administrador, 2=Almacen
                            if not rol or rol not in allowed_roles:
                                assigned_to = res_perm[1] if res_perm[1] else res_perm[2]
                                return False, f"Acceso denegado. Herramienta asignada permanentemente a {assigned_to}. Solo administradores o almacenistas pueden cambiarla."
                    
                    sql1 = "SELECT id FROM user WHERE full_name = %s"
                    cur1.execute(sql1, (nombre,))
                    res1 = cur1.fetchone()
                    if res1 is not None:
                        idUs = res1[0]
                        
                        # Determinar tipo de asignación
                        assignment_type = 'permanente' if accion == "cambio de propietario" else 'temporal'
                        
                        sql2 = "INSERT INTO movements(tool_id,user_id,action,person,location,observations,timestamp,assignment_type) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"
                        datos = (
                            idH,
                            idUs,
                            accion,
                            nombrer,
                            local,
                            obs,
                            datetime.now(),
                            assignment_type
                        )
                        cur2.execute(sql2, datos)
                        Conn.commit()
                        if accion == "entrada":
                            return True, "Devuelta con exito"
                        elif accion == "salida":
                            return True, "Prestamo exitoso"
                        else:
                            return True, "Movimiento registrado"
                    else:
                        return False, 'No se encontro el usuario'
                else:
                    return False, 'No se encontro la herramienta'

            except Error as e:
                Conn.rollback()
                return False, str(e)
            finally:
                cur.close()
                cur1.close()
                cur2.close()
                cur3.close()
                Conn.close()
    
    def estatusMov(self,herra) -> tuple[bool, list]:
        """Lo que checa esta funcion es el estatus de las herramientas para futuras validaciones"""
        db = Conexion()
        ok, Conn = db.conectar()
        if not ok:
            return False, Conn
        else:
            try:
                cur=Conn.cursor()
                cur1=Conn.cursor()
                sql="SELECT id, status FROM tools WHERE internal_code = %s AND status <> 'eliminada'"#obtengo el id de la herramienta para poder filtrar los  al igual que su status para evaluarlo
                cur.execute(sql,(herra,))
                res=cur.fetchone()
                if res is  None:
                    return False, 'No se encontro el id de la herramienta'
                idh, sts= res
                estatus_invalidos = ['en_reparacion', 'extraviada', 'obsoleta']
                if sts in estatus_invalidos:#valido que estatus tiene
                    return False, sts#si tiene alguno de estos 3 manda error
                sql1="SELECT action FROM movements WHERE tool_id = %s ORDER BY timestamp DESC LIMIT 1"#consulto la accion para poder evitar problemas de insercion
                cur1.execute(sql1,(idh,))
                res1=cur1.fetchone()
                if res1 is None:
                    return False,'No se encontro registro de la herramienta'
                acc=res1[0]
                return True, acc
            except Error as e:
                return False, str(e)
            finally:
                cur.close()
                cur1.close()
                Conn.close()
