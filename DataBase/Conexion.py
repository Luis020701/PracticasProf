"""hago uso de la clase de mysql para la Conexión"""
import dataclasses
import mysql.connector
@dataclasses.dataclass
class Conexion:
    """Creo la clase conexion para hacer uso de las funciones"""
    Con = mysql.connector.connect(
        host='localhost',
        user='root',
        password='gohanssj2',
        database='inventario'
    )

