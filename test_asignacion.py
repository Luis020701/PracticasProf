#!/usr/bin/env python3
"""Test para verificar que la asignación permanente acepta nombres personalizados"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Controlador.AsignacionesPermanentes import AsignacionesPermanentes
from Controlador.AltaHerramientas import AltaHerramientas
from DataBase.Conexion import Conexion

def test_asignacion_permanente():
    """Test de asignación permanente con nombre personalizado"""
    
    # Primero verificamos que tenemos una herramienta en BD
    db = Conexion()
    ok, conn = db.conectar()
    if not ok:
        print(f"Error de conexión: {conn}")
        return
    
    try:
        cur = conn.cursor(dictionary=True)
        
        # Obtener una herramienta existente
        cur.execute("SELECT internal_code FROM tools WHERE status <> 'eliminada' LIMIT 1")
        res = cur.fetchone()
        
        if not res:
            print("No hay herramientas en la BD para testear")
            conn.close()
            return
        
        codigo_herramienta = res['internal_code']
        print(f"Herramienta de test: {codigo_herramienta}")
        
        # Obtener un usuario existente para admin
        cur.execute("SELECT full_name FROM user LIMIT 1")
        res_user = cur.fetchone()
        
        if not res_user:
            print("No hay usuarios en la BD")
            conn.close()
            return
        
        usuario_admin = res_user['full_name']
        print(f"Usuario admin: {usuario_admin}")
        
        # Desactivar cualquier asignación permanente anterior
        cur.execute(
            "UPDATE permanent_assignments SET active=0 WHERE tool_id IN (SELECT id FROM tools WHERE internal_code=%s)",
            (codigo_herramienta,)
        )
        conn.commit()
        print(f"✓ Asignaciones previas desactivadas\n")
        
        conn.close()
        
        # Test 1: Usuario existente
        print("\n" + "="*50)
        print("Test 1: Asignación a usuario existente")
        print("="*50)
        asig = AsignacionesPermanentes()
        ok, msg = asig.marcar_asignacion_permanente(
            codigo_herramienta, 
            usuario_admin, 
            'auto', 
            usuario_admin
        )
        print(f"Resultado: {'✓' if ok else '✗'} {msg}")
        
        # Desmarcar para el siguiente test
        if ok:
            db2 = Conexion()
            ok2, conn2 = db2.conectar()
            if ok2:
                cur2 = conn2.cursor()
                cur2.execute("UPDATE permanent_assignments SET active=0 WHERE tool_id IN (SELECT id FROM tools WHERE internal_code=%s)", (codigo_herramienta,))
                conn2.commit()
                conn2.close()
        
        # Test 2: Nombre personalizado (no existe en BD)
        print("\n" + "="*50)
        print("Test 2: Asignación a nombre personalizado")
        print("="*50)
        asig2 = AsignacionesPermanentes()
        ok2, msg2 = asig2.marcar_asignacion_permanente(
            codigo_herramienta, 
            "Juan Personalizado", 
            'auto', 
            usuario_admin
        )
        print(f"Resultado: {'✓' if ok2 else '✗'} {msg2}")
        
        if ok2:
            # Verificar que se guardó correctamente
            db3 = Conexion()
            ok3, conn3 = db3.conectar()
            if ok3:
                cur3 = conn3.cursor(dictionary=True)
                cur3.execute(
                    "SELECT responsable_name, assignment_type, user_id, mochila_id FROM permanent_assignments WHERE tool_id IN (SELECT id FROM tools WHERE internal_code=%s) AND active=1",
                    (codigo_herramienta,)
                )
                res_asig = cur3.fetchone()
                if res_asig:
                    print(f"\n✓ Asignación guardada correctamente:")
                    print(f"  - Nombre: {res_asig['responsable_name']}")
                    print(f"  - Tipo: {res_asig['assignment_type']}")
                    print(f"  - User ID: {res_asig['user_id']}")
                    print(f"  - Mochila ID: {res_asig['mochila_id']}")
                conn3.close()
        
        print("\n" + "="*50)
        print("✅ Tests completados")
        print("="*50)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_asignacion_permanente()
