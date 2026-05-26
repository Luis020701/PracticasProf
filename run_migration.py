#!/usr/bin/env python3
"""Script para ejecutar la migración de BD"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from DataBase.Conexion import Conexion

def ejecutar_migracion():
    """Lee y ejecuta el script de migración"""
    db = Conexion()
    ok, conn = db.conectar()
    
    if not ok:
        print(f"Error de conexión: {conn}")
        return False
    
    try:
        with open('DataBase/migrations_permanent_assignments.sql', 'r', encoding='utf-8') as f:
            script = f.read()
        
        # Dividir el script en sentencias individuales
        sentencias = [s.strip() for s in script.split(';') if s.strip()]
        
        cur = conn.cursor()
        for i, sentencia in enumerate(sentencias, 1):
            # Ignorar comentarios de línea
            if sentencia.startswith('--'):
                continue
                
            print(f"Ejecutando sentencia {i}...")
            try:
                cur.execute(sentencia)
                conn.commit()
                print(f"✓ Sentencia {i} completada")
            except Exception as e:
                # Ignorar errores de "columna ya existe"
                if 'already exists' in str(e) or 'Duplicate column' in str(e):
                    print(f"⚠ Sentencia {i}: {e} (ignorado)")
                else:
                    print(f"✗ Error en sentencia {i}: {e}")
                    conn.rollback()
        
        cur.close()
        conn.close()
        print("\n✅ Migración completada")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == '__main__':
    ejecutar_migracion()
