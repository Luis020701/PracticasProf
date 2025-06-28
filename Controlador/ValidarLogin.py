"""Importo la Clase Conexion para poder trabajar con la Base de datos"""
import dataclasses
from werkzeug.security import generate_password_hash,check_password_hash
from DataBase.Conexion import Conexion
@dataclasses.dataclass
class ValidarLogin:
    """Creo la clase Validar Login para poder interactuar con este archivo"""
    def validaruser(self, user):
        """Funcion para validar el usuario"""
        db = Conexion()
        ok, Conn = db.conectar()
        if not ok:
            return False, Conn
        else:
            cur=Conn.cursor()
            sql = "SELECT username from user WHERE username = %s"
            cur.execute(sql,(user,))
            resultado = cur.fetchone()
            cur.close()
            return True, resultado
    def validapswd(self, pswd, user):
        """Funcion para validar la contraseña"""
        db = Conexion()
        ok, Conn = db.conectar()
        if not ok:
            return False, Conn
        else: 
            cur=Conn.cursor()
            #sql="SELECT password_hash from user WHERE password_hash = %s  AND username = %s"
            sql="SELECT password_hash from user WHERE username = %s"
            cur.execute(sql,(user,))
            resultado = cur.fetchone() 
            if not resultado:
                cur.close()
                return False, resultado
            else:
                pswdin = str(resultado[0])
                cur.close()
                return True, check_password_hash(pswdin,pswd)
    def obtenernombre(self,user):
        """Obtengo el nombre de el usuario de la base de datos para guardarlo en sesion"""
        db = Conexion()
        ok, Conn = db.conectar()
        if not ok:
            return False, Conn
        else: 
            cur=Conn.cursor()
            sql="SELECT * FROM user WHERE username = %s"
            cur.execute(sql,(user,))
            datos=cur.fetchone()
            cur.close()
            return True, datos
