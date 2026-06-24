-- Crear tipos ENUM para el estado de las acuarelas
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'watercolor_status') THEN
        CREATE TYPE watercolor_status AS ENUM ('DISPONIBLE', 'RESERVADO', 'COLECCION_PRIVADA');
    END IF;
END $$;

-- Tabla de Categorías/Colecciones (Paisajes, Retratos, Flores, etc.)
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla Principal: Catálogo de Acuarelas
CREATE TABLE IF NOT EXISTS watercolors (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    width_cm NUMERIC(5,2),
    height_cm NUMERIC(5,2),
    price NUMERIC(10,2), -- Puede ser NULL si es de colección privada y no tiene precio comercial
    image_url VARCHAR(512), -- Ruta en un storage o CDN
    status watercolor_status DEFAULT 'DISPONIBLE',
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para la gestión de memoria del Agente de IA (Fase 2)
-- Guardará el contexto de las conversaciones por el identificador del usuario (ej. número de teléfono)
CREATE TABLE IF NOT EXISTS ai_chat_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL UNIQUE, -- Identificador único (ej: whatsapp:+34xxxxxxxxx)
    chat_history JSONB NOT NULL DEFAULT '[]'::jsonb, -- Almacena la estructura de mensajes de LangChain
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para registrar Leads / Intenciones de Compra detectadas
CREATE TABLE IF NOT EXISTS purchase_leads (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) REFERENCES ai_chat_sessions(session_id) ON DELETE CASCADE,
    watercolor_id INTEGER REFERENCES watercolors(id) ON DELETE CASCADE,
    customer_contact VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'PENDIENTE_CONTACTO', -- PENDIENTE, EN_PROCESO, COMPLETADO
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Función y Trigger para actualizar automáticamente el campo 'updated_at'
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE OR REPLACE TRIGGER update_watercolors_updated_at
    BEFORE UPDATE ON watercolors
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE OR REPLACE TRIGGER update_ai_sessions_updated_at
    BEFORE UPDATE ON ai_chat_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- INSERCIÓN DE DATOS DE PRUEBA (Semillas / Seeders)
-- =============================================================================

INSERT INTO categories (name, description) VALUES
('Paisajes', 'Acuarelas inspiradas en la naturaleza, campos y entornos urbanos'),
('Flores y Botánica', 'Estudios detallados y composiciones florales'),
('Marinas', 'Escenas costeras, playas y el mar');

INSERT INTO watercolors (title, description, width_cm, height_cm, price, image_url, status, category_id) VALUES
('Atardecer en la Alcarria', 'Campos de lavanda durante el ocaso con tonos violetas intensos.', 40.00, 30.00, 250.00, 'https://storage.googleapis.com/galeria-ejemplo/lavanda.jpg', 'DISPONIBLE', 1),
('Reflejos en el Agua', 'Marina capturando la luz del amanecer sobre el puerto.', 50.00, 35.00, 320.00, 'https://storage.googleapis.com/galeria-ejemplo/marina1.jpg', 'RESERVADO', 3),
('Ramo de Hortensias', 'Estudio clásico de hortensias en tonos azules y blancos. Obra personal.', 30.00, 30.00, NULL, 'https://storage.googleapis.com/galeria-ejemplo/hortensias.jpg', 'COLECCION_PRIVADA', 2);