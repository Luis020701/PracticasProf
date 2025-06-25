"""Importo la libreria dataclases para clases con pocos metodos"""
import dataclasses

@dataclasses.dataclass
class Config:
    """Genero una llave para el manejo de datos"""
    SECRET_KEY = '$#V4oP#f3bPEZbXKSSSf!U'

@dataclasses.dataclass
class DevelopmentConfig(Config):
    """Con esta clase creo la configuracion de el inicio del servidor en modo DEBUGGER"""
    DEBUG=True
Config={
    'development':DevelopmentConfig
}
