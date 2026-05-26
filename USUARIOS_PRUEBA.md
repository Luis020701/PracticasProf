# 👥 USUARIOS DE PRUEBA - REFERENCIA DE CREDENCIALES

## 🔐 Usuarios Disponibles para Testing

### Administradores (Acceso completo)
| Usuario | Contraseña | Nombre Completo |
|---------|-----------|-----------------|
| admin_test | admin123 | Admin Test |
| admin_juan | juan2024 | Juan Pérez |

**Permisos:** Crear, editar, eliminar herramientas y mochilas, gestionar usuarios, acceder a reportes

---

### Almacenistas (Gestión de inventario)
| Usuario | Contraseña | Nombre Completo |
|---------|-----------|-----------------|
| almacen_test | almacen123 | Almacenista Test |
| almacen_carlos | carlos2024 | Carlos López |
| almacen_pedro | pedro2024 | Pedro Martínez |

**Permisos:** Crear herramientas, registrar movimientos, gestionar mochilas

---

### Instaladores (Acceso limitado)
| Usuario | Contraseña | Nombre Completo |
|---------|-----------|-----------------|
| instalador_test | instalador123 | Instalador Test |
| instalador_maria | maria2024 | María García |

**Permisos:** Consultar su inventario asignado y registrar préstamos de herramientas o mochilas completas. No puede modificar ni eliminar préstamos ya asignados ni desasignarse herramientas.

---

## 📝 Usuarios Preexistentes

Además de los usuarios de prueba, existen estos usuarios originales:

| Usuario | Nombre Completo | Rol |
|---------|-----------------|-----|
| jdoe | John Doe | Almacén |
| LRodriguez | Luis Humberto | Almacén |
| Alfredo | Alfredo Rodriguez | Almacén |

---

## 🧪 Escenarios de Prueba Recomendados

## 🔒 Matriz de permisos

| Rol | Permisos principales |
|-----|----------------------|
| Administrador | Acceso completo: herramientas, usuarios, mochilas, ubicaciones, asignaciones y reportes |
| Almacenista | Acceso a todos los módulos operativos: herramientas, mochilas, asignaciones, préstamos e inventario |
| Instalador | Consulta solo su inventario asignado y registra préstamos de herramientas o mochilas completas |

El instalador no puede modificar ni eliminar préstamos ya asignados. En formularios de préstamo, el responsable queda fijado a su usuario y la opción de devolución/desasignación queda bloqueada.

### 1. Crear asignación permanente
- **Usuario:** admin_test / admin123
- **Acción:** Crear una herramienta con asignación permanente a alguno de los almacenistas
- **Verificar:** Que el nombre personalizado se guarde correctamente

### 2. Intentar cambiar propietario (Admin)
- **Usuario:** admin_test / admin123
- **Acción:** Editar una herramienta con asignación permanente
- **Verificar:** Que se permita el cambio (admin tiene permisos)

### 3. Intentar devolver/desasignar herramienta (Instalador)
- **Usuario:** instalador_test / instalador123
- **Acción:** Intentar cambiar el propietario de una herramienta
- **Verificar:** Que se deniegue la devolución/desasignación desde su rol

### 4. Registrar movimientos
- **Usuario:** almacen_carlos / carlos2024
- **Acción:** Registrar entrada/salida de herramientas
- **Verificar:** Que aparezca su nombre en el historial

### 5. Consultar historial con filtros
- **Usuario:** admin_juan / juan2024
- **Acción:** Filtrar historial por persona responsable (usar nombres de la lista)
- **Verificar:** Que aparezcan los autocompletados

---

## 📊 Resumen de Acceso

```
┌─────────────────────────────────────────────────────┐
│ ROL              │ ID │ USUARIOS                    │
├──────────────────┼────┼─────────────────────────────┤
│ Administrador    │ 1  │ admin_test, admin_juan      │
│ Almacén          │ 2  │ almacen_test, almacen_carlos, almacen_pedro │
│ Instalador       │ 3  │ instalador_test, instalador_maria │
└─────────────────────────────────────────────────────┘
```

---

## 🔧 Para crear más usuarios

Ejecuta nuevamente el script:
```bash
python crear_usuarios_prueba.py
```

Este script es idempotente (seguro ejecutar varias veces - no duplicará usuarios existentes).

---

## 💡 Notas

- Las contraseñas están hasheadas con Werkzeug, compatible con `check_password_hash`
- Todos los usuarios están marcados como activos (is_active = 1)
- Los nombres de usuario deben ser únicos
- Para propósitos de prueba, se pueden cambiar directamente desde la BD

