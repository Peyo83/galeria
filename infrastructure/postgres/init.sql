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
-- 2. AUTENTICACIÓN Y USUARIOS (ADMINISTRACIÓN CMS v1)
-- =============================================================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE, -- Crea índice B-Tree único implícito
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 3. ESTRUCTURA DE CATÁLOGO Y SEO
-- =============================================================================
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(120) NOT NULL UNIQUE, -- Crea índice B-Tree único implícito
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS watercolors (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(280) NOT NULL UNIQUE, -- Crea índice B-Tree único implícito
    description TEXT,
    width_cm NUMERIC(5,2),
    height_cm NUMERIC(5,2),
    price NUMERIC(10,2),
    
    -- SEO de Imágenes: Path base sin extensión para resoluciones dinámicas
    image_base_path VARCHAR(512) NOT NULL, 
    alt_text VARCHAR(255) NOT NULL,
    
    status artwork_status DEFAULT 'DISPONIBLE',
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 4. ÍNDICES SECUNDARIOS NO ÚNICOS (OPTIMIZACIÓN DE LECTURA)
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_watercolors_status ON watercolors(status);
CREATE INDEX IF NOT EXISTS idx_watercolors_category_id ON watercolors(category_id);

-- =============================================================================
-- 5. AUTOMATIZACIÓN DE METADATOS
-- =============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_watercolors_updated_at ON watercolors;

CREATE TRIGGER update_watercolors_updated_at
    BEFORE UPDATE ON watercolors
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
