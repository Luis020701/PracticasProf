"""Importo la Clase Conexion para poder trabajar con la Base de datos"""
import dataclasses
from werkzeug.security import generate_password_hash,check_password_hash
from DataBase.Conexion import Conexion
@dataclasses.dataclass
class ValidarLogin:
    """Creo la clase Validar Login para poder interactuar con este archivo"""
    db = Conexion()
    Conn = db.conectar()
    cur=Conn.cursor()
    def validaruser(self, user):
        """Funcion para validar el usuario"""
        sql = "SELECT username from user WHERE username = %s"
        self.cur.execute(sql,(user,))
        resultado = self.cur.fetchone()
        return resultado
    def validapswd(self, pswd, user):
        """Funcion para validar la contraseña"""
        paswd_hash=generate_password_hash(pswd)
        #sql="SELECT password_hash from user WHERE password_hash = %s  AND username = %s"
        sql="SELECT password_hash from user WHERE username = %s"
        self.cur.execute(sql,(user,))
        pswdin = str(self.cur.fetchone()[0])
        return check_password_hash(pswdin,pswd)
    def obtenernombre(self,user):
        """Obtengo el nombre de el usuario de la base de datos para guardarlo en sesion"""
        sql="SELECT * FROM user WHERE username = %s"
        self.cur.execute(sql,(user,))
        datos=self.cur.fetchone()
        return datos
       
    def cerrarcursor(self):
        """cierro cursor a la base de datos"""
        self.cur.close()
