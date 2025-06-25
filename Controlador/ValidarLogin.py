"""Importo la Clase Conexion para poder trabajar con la Base de datos"""
import dataclasses
from werkzeug.security import generate_password_hash,check_password_hash
from DataBase.Conexion import Conexion
@dataclasses.dataclass
class ValidarLogin:
    """Creo la clase Validar Login para poder interactuar con este archivo"""
    Conn = Conexion.Con.cursor()
    def validaruser(self, user):
        """Funcion para validar el usuario"""
        sql = "SELECT username from user WHERE username = %s"
        self.Conn.execute(sql,(user,))
        resultado = self.Conn.fetchone()
        return resultado
    def validapswd(self, pswd, user):
        """Funcion para validar la contraseña"""
        paswd_hash=generate_password_hash(pswd)
        #sql="SELECT password_hash from user WHERE password_hash = %s  AND username = %s"
        sql="SELECT password_hash from user WHERE username = %s"
        self.Conn.execute(sql,(user,))
        pswdin = str(self.Conn.fetchone()[0])
        return check_password_hash(pswdin,pswd)
    def obtenernombre(self,user):
        """Obtengo el nombre de el usuario de la base de datos para guardarlo en sesion"""
        sql="SELECT * FROM user WHERE username = %s"
        self.Conn.execute(sql,(user,))
        datos=self.Conn.fetchone()
        return datos
        
    def cerrarcursor(self):
        """cierro cursor a la base de datos"""
        self.Conn.close()