-- Script para crear la tabla de asignaciones permanentes
-- Ejecutar en MySQL con base de datos 'inventario'

CREATE TABLE IF NOT EXISTS permanent_assignments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    tool_id INT NOT NULL,
    user_id INT,
    mochila_id INT,
    responsable_name VARCHAR(255),
    assignment_type ENUM('user', 'mochila') NOT NULL,
    assigned_by INT,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT 1,
    FOREIGN KEY (tool_id) REFERENCES tools(id),
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (mochila_id) REFERENCES mochilas(id_mochila),
    FOREIGN KEY (assigned_by) REFERENCES user(id),
    UNIQUE KEY unique_tool_assignment (tool_id)
);

-- Agregar columna responsable_name si no existe (para tabla existente)
ALTER TABLE permanent_assignments ADD COLUMN responsable_name VARCHAR(255) AFTER mochila_id;

-- Agregar columna a la tabla movements para diferenciar tipo de asignación
ALTER TABLE movements ADD COLUMN assignment_type ENUM('permanente', 'temporal') DEFAULT 'temporal' AFTER observations;

-- Permitir acciones usadas por el historial y las asignaciones permanentes
ALTER TABLE movements MODIFY action ENUM('entrada', 'salida', 'alta', 'cambio de propietario') NULL;

-- Crear índices para búsqueda rápida
CREATE INDEX idx_permanent_user ON permanent_assignments(user_id);
CREATE INDEX idx_permanent_mochila ON permanent_assignments(mochila_id);
CREATE INDEX idx_permanent_tool ON permanent_assignments(tool_id);
CREATE INDEX idx_permanent_active ON permanent_assignments(active);
