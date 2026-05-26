#!/usr/bin/env python3
"""Script para crear usuarios de prueba con distintos roles"""
import sys
import os
import unicodedata
from datetime import datetime
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from DataBase.Conexion import Conexion

def configurar_salida():
    """Permite imprimir acentos y emojis en consolas Windows."""
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

def hash_password(password):
    """Hashea una contraseña compatible con el login de Flask/Werkzeug"""
    return generate_password_hash(password)

def normalizar_rol(nombre):
    """Normaliza nombres de roles para comparar sin acentos ni mayúsculas."""
    texto = unicodedata.normalize("NFKD", nombre or "")
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.lower().strip()

def crear_usuarios_prueba():
    """Crea múltiples usuarios de prueba con distintos roles"""
    
    db = Conexion()
    ok, conn = db.conectar()
    
    if not ok:
        print(f"❌ Error de conexión: {conn}")
        return False
    
    try:
        cur = conn.cursor(dictionary=True)
        
        # Primero, verificar roles existentes
        print("="*60)
        print("📋 VERIFICANDO ROLES EXISTENTES")
        print("="*60)
        
        cur.execute("SHOW TABLES LIKE 'role%'")
        if cur.fetchone():
            cur.execute("SELECT * FROM roles")
            roles = cur.fetchall()
            for role in roles:
                if normalizar_rol(role.get('name')) == "tecnico":
                    cur.execute("UPDATE roles SET name = %s WHERE id = %s", ("Instalador", role.get('id')))
                    conn.commit()
                    role["name"] = "Instalador"
            print(f"✓ Tabla de roles encontrada ({len(roles)} roles)")
            for role in roles:
                print(f"  ID: {role.get('id', 'N/A')}, Nombre: {role.get('name', 'N/A')}")
            role_ids = {normalizar_rol(role.get('name', '')): role.get('id') for role in roles}
        else:
            print("⚠ No existe tabla 'roles'. Usando role_id directo según código de índices.py")
            # Del código de index.py: ROLES = {"Administrador":1, "Almacen":2, "Instalador":3}
            role_ids = {"administrador": 1, "almacen": 2, "instalador": 3, "tecnico": 3}
            print("  Roles del sistema:")
            print("    ID 1: Administrador")
            print("    ID 2: Almacén")
            print("    ID 3: Instalador")
        
        # Usuarios de prueba a crear
        usuarios_prueba = [
            {
                "username": "admin_test",
                "full_name": "Admin Test",
                "password": "admin123",
                "role_id": role_ids.get("administrador", 1),
                "role_name": "Administrador"
            },
            {
                "username": "almacen_test",
                "full_name": "Almacenista Test",
                "password": "almacen123",
                "role_id": role_ids.get("almacen", 2),
                "role_name": "Almacén"
            },
            {
                "username": "instalador_test",
                "full_name": "Instalador Test",
                "password": "instalador123",
                "role_id": role_ids.get("instalador", role_ids.get("tecnico", 3)),
                "role_name": "Instalador"
            },
            {
                "username": "admin_juan",
                "full_name": "Juan Pérez",
                "password": "juan2024",
                "role_id": role_ids.get("administrador", 1),
                "role_name": "Administrador"
            },
            {
                "username": "almacen_carlos",
                "full_name": "Carlos López",
                "password": "carlos2024",
                "role_id": role_ids.get("almacen", 2),
                "role_name": "Almacén"
            },
            {
                "username": "instalador_maria",
                "full_name": "María García",
                "password": "maria2024",
                "role_id": role_ids.get("instalador", role_ids.get("tecnico", 3)),
                "role_name": "Instalador"
            },
            {
                "username": "almacen_pedro",
                "full_name": "Pedro Martínez",
                "password": "pedro2024",
                "role_id": role_ids.get("almacen", 2),
                "role_name": "Almacén"
            },
        ]
        
        print("\n" + "="*60)
        print("➕ CREANDO USUARIOS DE PRUEBA")
        print("="*60)
        
        creados = 0
        duplicados = 0
        errores = 0
        
        for usuario in usuarios_prueba:
            try:
                # Verificar si el usuario ya existe
                cur.execute("SELECT id FROM user WHERE username = %s", (usuario["username"],))
                if cur.fetchone():
                    print(f"⚠ Usuario '{usuario['username']}' ya existe (duplicado)")
                    duplicados += 1
                    continue
                
                # Hash de la contraseña
                password_hash = hash_password(usuario["password"])
                
                # Insertar usuario
                sql = """
                    INSERT INTO user (username, password_hash, full_name, role_id, created_at, is_active)
                    VALUES (%s, %s, %s, %s, %s, 1)
                """
                cur.execute(sql, (
                    usuario["username"],
                    password_hash,
                    usuario["full_name"],
                    usuario["role_id"],
                    datetime.now()
                ))
                conn.commit()
                
                print(f"✓ Usuario creado: '{usuario['username']}' ({usuario['role_name']})")
                print(f"  - Nombre: {usuario['full_name']}")
                print(f"  - Contraseña: {usuario['password']}")
                creados += 1
                
            except Exception as e:
                print(f"✗ Error al crear '{usuario['username']}': {e}")
                errores += 1
                conn.rollback()
        
        print("\n" + "="*60)
        print("📊 RESUMEN")
        print("="*60)
        print(f"✓ Creados: {creados}")
        print(f"⚠ Duplicados (no creados): {duplicados}")
        print(f"✗ Errores: {errores}")
        
        # Mostrar todos los usuarios
        print("\n" + "="*60)
        print("👥 TODOS LOS USUARIOS EN EL SISTEMA")
        print("="*60)
        
        cur.execute("""
            SELECT u.id, u.username, u.full_name, u.role_id, u.is_active
            FROM user u
            ORDER BY u.id
        """)
        
        usuarios = cur.fetchall()
        for u in usuarios:
            role_name = {1: "Admin", 2: "Almacén", 3: "Instalador"}.get(u['role_id'], "Desconocido")
            estado = "✓ Activo" if u['is_active'] else "✗ Inactivo"
            print(f"ID {u['id']:2d} | {u['username']:20s} | {u['full_name']:25s} | {role_name:10s} | {estado}")
        
        conn.close()
        
        if creados > 0:
            print("\n" + "="*60)
            print("✅ USUARIOS DE PRUEBA CREADOS EXITOSAMENTE")
            print("="*60)
            print("\nPuede usar estos usuarios para iniciar sesión:")
            for usuario in usuarios_prueba[:3]:
                print(f"  Usuario: {usuario['username']}")
                print(f"  Contraseña: {usuario['password']}\n")
            return True
        else:
            print("\n⚠ No se crearon usuarios nuevos")
            return False
            
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    configurar_salida()
    crear_usuarios_prueba()
