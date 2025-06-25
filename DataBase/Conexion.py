"""hago uso de la clase de mysql para la Conexión"""
import dataclasses
import mysql.connector
from mysql.connector import Error
@dataclasses.dataclass
class Conexion:
    """Creo la clase conexion para hacer uso de las funciones"""
    def conectar(self): 
        """Funcion para conectar""" 
        try:
            Con = mysql.connector.connect(
                host='localhost',
                user='root',
                password='gohanssj2',
                database='inventario'
            )
            if Con.is_connected():
                return Con
        except Error as e:
            return e