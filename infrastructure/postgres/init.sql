-- =============================================================================
-- 1. TIPOS ENUM Y CONFIGURACIÓN INICIAL
-- =============================================================================
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'artwork_status') THEN
        CREATE TYPE artwork_status AS ENUM ('DISPONIBLE', 'RESERVADO', 'COLECCION_PRIVADA');
    END IF;
END $$;

-- =============================================================================
-- 2. ESTRUCTURA DE TABLAS (MAESTRAS Y CATÁLOGO)
-- =============================================================================

-- Tabla de Categorías/Colecciones con soporte para URLs amigables
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(120) NOT NULL UNIQUE, -- URL Amigable: ej. /coleccion/paisajes
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla Principal: Catálogo de Acuarelas optimizado para SEO e indexación de imágenes
CREATE TABLE IF NOT EXISTS watercolors (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(280) NOT NULL UNIQUE, -- URL Amigable: ej. /obra/atardecer-en-la-alcarria
    description TEXT,
    width_cm NUMERIC(5,2),
    height_cm NUMERIC(5,2),
    price NUMERIC(10,2), -- Puede ser NULL si es de colección privada
    
    -- SEO de Imágenes: Path base para construir resoluciones dinámicas (srcset) en Nuxt 3 / CDN
    image_base_path VARCHAR(512) NOT NULL, 
    alt_text VARCHAR(255) NOT NULL, -- Atributo ALT descriptivo indexable
    
    status artwork_status DEFAULT 'DISPONIBLE',
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 3. PERSISTENCIA DE NEGOCIO E INTELIGENCIA ARTIFICIAL (FASE 2)
-- =============================================================================

-- Tabla para la gestión de memoria del Agente de IA (LangChain)
CREATE TABLE IF NOT EXISTS ai_chat_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL UNIQUE, -- Identificador único (ej: whatsapp:+34xxxxxxxxx)
    chat_history JSONB NOT NULL DEFAULT '[]'::jsonb, -- Estructura de mensajes asíncronos
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para registrar Leads / Intenciones de Compra detectadas por el agente
CREATE TABLE IF NOT EXISTS purchase_leads (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) REFERENCES ai_chat_sessions(session_id) ON DELETE CASCADE,
    watercolor_id INTEGER REFERENCES watercolors(id) ON DELETE CASCADE,
    customer_contact VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'PENDIENTE_CONTACTO', -- PENDIENTE_CONTACTO, EN_PROCESO, COMPLETADO
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 4. OPTIMIZACIÓN DE RENDIMIENTO (ÍNDICES)
-- =============================================================================
-- Índices críticos para la resolución de rutas SSR en Nuxt 3 y queries asíncronas en FastAPI
CREATE INDEX IF NOT EXISTS idx_categories_slug ON categories(slug);
CREATE INDEX IF NOT EXISTS idx_watercolors_slug ON watercolors(slug);
CREATE INDEX IF NOT EXISTS idx_watercolors_status ON watercolors(status);

-- =============================================================================
-- 5. AUTOMATIZACIÓN DE METADATOS (TRIGGERS)
-- =============================================================================
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
-- 6. SEMILLAS DE DATOS (SEEDERS DE PRUEBA)
-- =============================================================================
INSERT INTO categories (name, slug, description) VALUES
('Paisajes', 'paisajes', 'Acuarelas inspiradas en la naturaleza, campos y entornos urbanos'),
('Flores y Botánica', 'flores-y-botanica', 'Estudios detallados y composiciones florales'),
('Marinas', 'marinas', 'Escenas costeras, playas y el mar')
ON CONFLICT (slug) DO NOTHING;

INSERT INTO watercolors (title, slug, description, width_cm, height_cm, price, image_base_path, alt_text, status, category_id) VALUES
('Atardecer en la Alcarria', 'atardecer-en-la-alcarria', 'Campos de lavanda durante el ocaso con tonos violetas intensos.', 40.00, 30.00, 250.00, 'obras/lavanda', 'Pintura en acuarela de campos de lavanda en la Alcarria durante el atardecer', 'DISPONIBLE', 1),
('Reflejos en el Agua', 'reflejos-en-el-agua', 'Marina capturando la luz del amanecer sobre el puerto.', 50.00, 35.00, 320.00, 'obras/marina1', 'Acuarela marina que muestra reflejos de luz solar matutina en el agua del puerto', 'RESERVADO', 3),
('Ramo de Hortensias', 'ramo-de-hortensias', 'Estudio clásico de hortensias en tonos azules y blancos. Obra personal.', 30.00, 30.00, NULL, 'obras/hortensias', 'Estudio botánico en acuarela de un ramo de hortensias azules y blancas', 'COLECCION_PRIVADA', 2)
ON CONFLICT (slug) DO NOTHING;