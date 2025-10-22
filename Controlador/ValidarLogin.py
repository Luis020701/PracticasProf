"""Importo la Clase Conexion para poder trabajar con la Base de datos"""
import dataclasses
from werkzeug.security import generate_password_hash,check_password_hash
from DataBase.Conexion import Conexion, Error
@dataclasses.dataclass
class ValidarLogin:
    """Creo la clase Validar Login para poder interactuar con este archivo"""
    def validaruser(self, user) -> tuple[bool, list]:
        """Funcion para validar el usuario"""
        db = Conexion()
        ok, Conn = db.conectar()
        if not ok:
            return False, Conn
        else:
            cur=Conn.cursor()
            sql = "SELECT username from user WHERE username = %s"
            try:#El try evalua la sentencia y ejecuta el codigo en caso de que funcione
                cur.execute(sql,(user,))
                resultado = cur.fetchone()
                return True, resultado
            except Error as e:#except regresa False para indicar el error e indica cual es el error con la variable e
                return False, str(e)
            finally:#ejecuta si o si el cerrado del cursor para no dejarlo abierto
                cur.close()
                Conn.close()
    def validapswd(self, pswd, user) -> tuple[bool, list]:
        """Funcion para validar la contraseña"""
        db = Conexion()
        ok, Conn = db.conectar()
        if not ok:
            return False, Conn
        else: 
            cur=Conn.cursor()
            #sql="SELECT password_hash from user WHERE password_hash = %s  AND username = %s"
            sql="SELECT password_hash from user WHERE username = %s"
            try:#El try evalua la sentencia y ejecuta el codigo en caso de que funcione
                cur.execute(sql,(user,))
                resultado = cur.fetchone() 
                if not resultado:
                    return False, resultado
                else:
                    pswdin = str(resultado[0])
                    return True, check_password_hash(pswdin,pswd)
            except Error as e:#except regresa False para indicar el error e indica cual es el error con la variable e
                return False, str(e)
            finally:#ejecuta si o si el cerrado del cursor para no dejarlo abierto
                cur.close()
                Conn.close()
    def obtenernombre(self,user) -> tuple[bool, list]:
        """Obtengo el nombre de el usuario de la base de datos para guardarlo en sesion"""
        db = Conexion()
        ok, Conn = db.conectar()
        if not ok:
            return False, Conn
        else: 
            try:#El try evalua la sentencia y ejecuta el codigo en caso de que funcione
                cur=Conn.cursor()
                sql="SELECT * FROM user WHERE username = %s"
                cur.execute(sql,(user,))
                datos=cur.fetchone()
                return True, datos
            except Error as e:#except regresa False para indicar el error e indica cual es el error con la variable e
                return False, str(e)
            finally:#ejecuta si o si el cerrado del cursor para no dejarlo abierto
                cur.close()
                Conn.close()
