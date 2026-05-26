#!/usr/bin/env python3
"""Script para administrar usuarios de prueba"""
import sys
import os
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

def listar_usuarios():
    """Lista todos los usuarios"""
    db = Conexion()
    ok, conn = db.conectar()
    if not ok:
        print(f"Error: {conn}")
        return
    
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT u.id, u.username, u.full_name, u.role_id, u.is_active, r.name as role_name
        FROM user u
        LEFT JOIN roles r ON u.role_id = r.id
        ORDER BY u.role_id, u.id
    """)
    
    usuarios = cur.fetchall()
    print("\n" + "="*80)
    print("👥 USUARIOS DEL SISTEMA")
    print("="*80)
    print(f"{'ID':>3} {'Username':<20} {'Nombre':<25} {'Rol':<15} {'Estado':<10}")
    print("-"*80)
    
    for u in usuarios:
        role = "Instalador" if u.get('role_id') == 3 else (u.get('role_name', '').capitalize() if u.get('role_name') else "N/A")
        estado = "✓ Activo" if u['is_active'] else "✗ Inactivo"
        print(f"{u['id']:3d} {u['username']:<20} {u['full_name']:<25} {role:<15} {estado:<10}")
    
    print("="*80 + "\n")
    conn.close()

def cambiar_contrasena(username, nueva_contrasena):
    """Cambia la contraseña de un usuario"""
    db = Conexion()
    ok, conn = db.conectar()
    if not ok:
        print(f"Error: {conn}")
        return False
    
    try:
        cur = conn.cursor()
        password_hash = hash_password(nueva_contrasena)
        
        cur.execute("UPDATE user SET password_hash = %s WHERE username = %s", 
                   (password_hash, username))
        conn.commit()
        
        if cur.rowcount > 0:
            print(f"✓ Contraseña actualizada para '{username}'")
            return True
        else:
            print(f"✗ Usuario '{username}' no encontrado")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

def resetear_contrasenas():
    """Resetea las contraseñas de los usuarios de prueba a valores por defecto"""
    usuarios_reset = [
        ("admin_test", "admin123"),
        ("almacen_test", "almacen123"),
        ("instalador_test", "instalador123"),
        ("tecnico_test", "tecnico123"),
        ("admin_juan", "juan2024"),
        ("almacen_carlos", "carlos2024"),
        ("instalador_maria", "maria2024"),
        ("tecnico_maria", "maria2024"),
        ("almacen_pedro", "pedro2024"),
    ]
    
    print("\n" + "="*60)
    print("🔑 RESETEANDO CONTRASEÑAS")
    print("="*60)
    
    for username, password in usuarios_reset:
        if cambiar_contrasena(username, password):
            print(f"   Nueva contraseña: {password}")
    
    print("="*60 + "\n")

def activar_usuario(username):
    """Activa un usuario"""
    db = Conexion()
    ok, conn = db.conectar()
    if not ok:
        print(f"Error: {conn}")
        return False
    
    try:
        cur = conn.cursor()
        cur.execute("UPDATE user SET is_active = 1 WHERE username = %s", (username,))
        conn.commit()
        
        if cur.rowcount > 0:
            print(f"✓ Usuario '{username}' activado")
            return True
        else:
            print(f"✗ Usuario '{username}' no encontrado")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

def desactivar_usuario(username):
    """Desactiva un usuario"""
    db = Conexion()
    ok, conn = db.conectar()
    if not ok:
        print(f"Error: {conn}")
        return False
    
    try:
        cur = conn.cursor()
        cur.execute("UPDATE user SET is_active = 0 WHERE username = %s", (username,))
        conn.commit()
        
        if cur.rowcount > 0:
            print(f"✓ Usuario '{username}' desactivado")
            return True
        else:
            print(f"✗ Usuario '{username}' no encontrado")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

def menu():
    """Menú interactivo"""
    while True:
        print("\n" + "="*60)
        print("🔧 ADMINISTRACIÓN DE USUARIOS DE PRUEBA")
        print("="*60)
        print("1. Listar usuarios")
        print("2. Cambiar contraseña")
        print("3. Resetear todas las contraseñas")
        print("4. Activar usuario")
        print("5. Desactivar usuario")
        print("6. Salir")
        print("="*60)
        
        opcion = input("\nSelecciona una opción (1-6): ").strip()
        
        if opcion == "1":
            listar_usuarios()
        
        elif opcion == "2":
            username = input("Nombre de usuario: ").strip()
            nueva_pass = input("Nueva contraseña: ").strip()
            if username and nueva_pass:
                cambiar_contrasena(username, nueva_pass)
            else:
                print("❌ Entrada inválida")
        
        elif opcion == "3":
            confirmacion = input("¿Estás seguro? (s/n): ").strip().lower()
            if confirmacion == 's':
                resetear_contrasenas()
        
        elif opcion == "4":
            username = input("Nombre de usuario: ").strip()
            if username:
                activar_usuario(username)
        
        elif opcion == "5":
            username = input("Nombre de usuario: ").strip()
            if username:
                desactivar_usuario(username)
        
        elif opcion == "6":
            print("\n✓ Saliendo...\n")
            break
        
        else:
            print("❌ Opción inválida")

if __name__ == '__main__':
    configurar_salida()
    if len(sys.argv) > 1:
        # Modo línea de comandos
        comando = sys.argv[1].lower()
        
        if comando == "listar":
            listar_usuarios()
        elif comando == "resetear":
            resetear_contrasenas()
        elif comando == "cambiar" and len(sys.argv) >= 4:
            cambiar_contrasena(sys.argv[2], sys.argv[3])
        elif comando == "activar" and len(sys.argv) >= 3:
            activar_usuario(sys.argv[2])
        elif comando == "desactivar" and len(sys.argv) >= 3:
            desactivar_usuario(sys.argv[2])
        else:
            print("Uso:")
            print("  python admin_usuarios.py listar")
            print("  python admin_usuarios.py cambiar <username> <nueva_contrasena>")
            print("  python admin_usuarios.py resetear")
            print("  python admin_usuarios.py activar <username>")
            print("  python admin_usuarios.py desactivar <username>")
            print("\nO ejecuta sin argumentos para menú interactivo:")
            print("  python admin_usuarios.py")
    else:
        # Modo menú interactivo
        menu()
