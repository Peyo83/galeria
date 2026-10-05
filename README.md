# 🎨 Galería de Arte Online - Acuarelas

Sistema web completo de alta eficiencia para la exposición y catalogación de acuarelas. Diseñado desde la base con arquitectura SSR/Híbrida para maximizar el **SEO Técnico**, la velocidad de carga (**Core Web Vitals**) y la indexación en **Google Imágenes**, complementado con un panel de administración (CMS) privado.

---

## 📐 Estrategia de Despliegue y Arquitectura

El proyecto está estructurado en **dos fases principales** para garantizar una maduración previa del dominio y la indexación de obras antes de habilitar la capa transaccional:

### 🚀 Versión 1: Galería Expositiva & CMS Admin (FASE ACTUAL)
- **Frontend Expositivo:** Interfaz minimalista fluida en Nuxt 3 (SSR) centrada en resaltar la pintura en acuarela.
- **Panel de Administración (CMS):** Gestión de catálogo (obras y categorías), autenticación segura JWT y control de metadatos SEO.
- **SEO & Performance:** Inyección dinámica de datos estructurados Schema.org (`VisualArtwork` y `ArtGallery`), URLs amigables (`/obra/slug`) e imágenes responsive (`<picture>`, WebP/AVIF).
- **Core Backend:** FastAPI asíncrono con PostgreSQL (`postgres:15-alpine`).

### 🔮 Versión 2: Monetización, IA & Telemetría (ROADMAP FUTURO)
- **Motor Transaccional:** Apertura de venta directa y gestión de intenciones de compra (`purchase_leads`).
- **Agente IA & Automatización:** Asistente conversacional con LangChain e integración con WhatsApp a través de webhooks en n8n (`ai_chat_sessions`).
- **Pipeline de Big Data:** Streaming de eventos de navegación y telemetría en tiempo real con Apache Kafka.

---

## 🛠️ Stack Tecnológico (v1)

- **Backend:** Python 3.11+ | FastAPI | SQLModel / SQLAlchemy (AsyncSession) | JWT Auth
- **Frontend:** Nuxt 3 | TypeScript | CSS Grid/Flexbox (`rem`/`em`) | Pinia
- **Base de Datos:** PostgreSQL 15 Alpine (Contenerizado)
- **Infraestructura:** Docker & Docker Compose | Red aislada (`galeria_network_global`)
- **SEO & Analytics:** Schema.org JSON-LD | OpenGraph / Twitter Cards | DataLayer GA4/GTM

---

## 📂 Estructura del Proyecto

```text
GALERIA/
├── backend/                  # Código fuente FastAPI, SQLModel y lógica de negocio (v1/v2)
│   ├── app/                  # Módulos, endpoints, modelos y utilidades
│   ├── tests/                # Suites de pruebas unitarias e integración
│   ├── Dockerfile            # Construcción del contenedor Backend
│   └── requirements.txt      # Dependencias Python
├── frontend/                 # Código fuente Nuxt 3 + TypeScript
│   ├── Dockerfile            # Construcción del contenedor Frontend
│   └── package.json
├── automation/               # Workflows y configuración n8n (Fase v2)
│   └── docker/
├── infrastructure/           # Configuración de servicios de infraestructura
│   ├── postgres/             # Script de inicialización SQL y customizaciones DB
│   │   └── init.sql          # Esquema relacional optimizado v1
│   ├── kafka/                # Orquestación de brokers de eventos (Fase v2)
│   └── reverse-proxy/        # Configuración Nginx ingress / SSL
├── .env                      # Variables de entorno locales (git-ignored)
├── .env.example              # Plantilla de configuración de entorno
├── docker-compose.yml        # Orquestador global de servicios Docker
└── README.md                 # Documentación técnica de arquitectura

```

---

## 🚀 Guía de Inicio Rápido (Entorno Local)

### 1. Requisitos Previos

Clona la plantilla de entorno y ajusta las credenciales locales:

* Docker Desktop Engine v20.10+ instalado y corriendo en entorno Linux / WSL2.
* Docker Compose v2.x+.

### 2. Configuración de Variables de Entorno

Asegúrate de configurar los puertos y credenciales dentro de .env:

```bash
POSTGRES_USER=user
POSTGRES_PASSWORD=pass
POSTGRES_DB=db
POSTGRES_PORT=1234
OPENAI_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

### 3. Exportación de Variables en Shell (Linux / Bash / WSL2)

Antes de interactuar con Docker Compose o ejecutar scripts directos, exporta las variables:

```bash
export $(grep -v '^#' .env \vert{} grep -v '^$' | xargs)

```

### 4. Levantamiento de la Infraestructura

Inicia el stack contenerizado (Database + Backend):

```bash
# Iniciar servicios en segundo plano
docker compose up -d --build

# Verificar estado de los contenedores
docker compose ps

# Inspeccionar logs del sistema
docker compose logs -f

```

## 🗄️ Esquema de Base de Datos (v1)

El archivo infrastructure/postgres/init.sql inicializa automáticamente la estructura base con los siguientes componentes:

1. users: Administradores del sistema con contraseñas encriptadas para el CMS.
2. categories: Categorización semántica de obras (/coleccion/:slug).ç
3. watercolors: Ficha técnica de pinturas (dimensiones, estado, precio, rutas base de imágenes responsive y textos alt para SEO).
4. artwork_status (ENUM): Control de disponibilidad (DISPONIBLE, RESERVADO, COLECCION_PRIVADA).
5. Índices B-Tree: Optimización de consultas en campos slug para resolver peticiones SSR en tiempo constante $O(1)$.

---

## 🗺️ HOJA DE RUTA ARQUITECTÓNICA POR FASES

🔹 [x] Fase 1A: Infraestructura Docker aislada y esquema de base de datos PostgreSQL v1 (init.sql).
🔹 [ ] Fase 1B: API FastAPI v1 (Modelos SQLModel asíncronos, Auth JWT, Endpoints CRUD CMS, Manejo de imágenes WebP).
🔹 [ ] Fase 1C: Frontend Nuxt 3 v1 (Layout fluido, renderizado SSR, inyección JSON-LD Schema.org, Panel Admin).
🔹 [ ] Fase 2A (Roadmap): Persistencia de leads de compra y orquestación de agentes IA con LangChain.
🔹 [ ] Fase 2A (Roadmap): Persistencia de leads de compra y orquestación de agentes IA con LangChain.
🔹 [ ] Fase 2C (Roadmap): Pipeline de telemetría distribuida con Apache Kafka.
