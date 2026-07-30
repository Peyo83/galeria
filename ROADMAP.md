# 🗺️ CONTROL DE INGENIERÍA: HOJA DE RUTA DE LA GALERÍA

Este archivo es el registro vivo del desarrollo y la arquitectura evolutiva de la plataforma. Funciona como el mapa técnico centralizado para el desarrollo local y el contexto de agentes de IA.

---

# 📋 [FICHA GLOBAL DEL PROYECTO]

* **Propósito Principal:** Construcción de una plataforma web responsive (Nuxt 3 SSR) optimizada para SEO Técnico e indexación index-first de portafolios de acuarela, respaldada por un backend asíncrono (FastAPI), agentes de IA y automatización de leads.
* **Entorno Host:** Docker de desarrollo en WSL2 (Ubuntu) sobre una red global unificada (`galeria_network_global`).
* **Estado Actual:** 🔹 **Fase 1 (En Desarrollo - Core Base de Datos e Ingress)**

---

# 🪜 [SECUENCIA DE FASES DE DESARROLLO]

### 🔹 FASE 1: El Corazón, la Red y el Ingress (Docker & DB Core)
*   **🛠️ ¿Qué hace?:** Levanta la infraestructura de persistencia relacional base y el aislamiento de red del proyecto.
*   **🔑 Componentes Clave:**
    *   `postgres:15-alpine` + Volumen persistente (`galeria_postgres_data`).
    *   `init.sql`: Definición física de tablas (`categories`, `watercolors`, `ai_chat_sessions`, `purchase_leads`).
    *   Optimización index-first: Índices B-Tree en campos `slug` únicos y soporte nativo para metadatos `alt_text`.
    *   Nginx como Ingress/Reverse-Proxy local para orquestar la red sin problemas de CORS.
*   **💡 Nota de Diseño:** El contenedor de Postgres expone un puerto alternativo local (`1234`) para evitar conflictos de sistema y cuenta con un script de `healthcheck` (`pg_isready`) crítico para bloquear servicios dependientes.

### 🔹 FASE 2: El Backend y la Capa Cognitiva (FastAPI & LangGraph)
*   **🛠️ ¿Qué hace?:** Construye la API asíncrona de alto rendimiento y la lógica de los agentes de IA conversacionales.
*   **🔑 Componentes Clave:**
    *   Engine: FastAPI con concurrencia nativa a través de SQLAlchemy/SQLModel (`AsyncSession`).
    *   Estructuras SEO: Endpoints preparados para inyectar payloads JSON-LD (`VisualArtwork` y `ArtGallery`) directo desde el servidor.
    *   Orquestación de IA: Agentes inteligentes con persistencia de estado mediante LangGraph.
    *   Almacenamiento IA: Guardado del histórico de las sesiones conversacionales en formato `JSONB` en Postgres.
*   **💡 Nota de Diseño:** Se reconfigura Nginx para actuar como proxy inverso hacia la ruta `/api/v1`, eliminando la necesidad de habilitar CORS en el código de la API.

### 🔹 FASE 3: El Puente de Automatización (n8n & WhatsApp CRM)
*   **🛠️ ¿Qué hace?:** Automatiza la captura de leads interesados y conecta el ecosistema local con canales de mensajería externos.
*   **🔑 Componentes Clave:**
    *   Infraestructura: Instancia de n8n en contenedor conectada a la red interna compartida.
    *   Webhook de Entrada: Captura en tiempo real de interacciones desde la API de WhatsApp.
    *   Router Lógico: Envío del string de texto al agente de FastAPI para analizar la intención de compra.
    *   Disparador de Alertas: Notificación y flujo automático cuando el lead transiciona a estado `PENDIENTE_CONTACTO`.
*   **💡 Nota de Diseño:** Los flujos de n8n se aíslan en la red interna para que solo expongan el webhook específico de recepción de mensajes.

### 🔹 FASE 4: Rompiendo el Cuello de Botella Frontend (Nuxt 3 + TypeScript)
*   **🛠️ ¿Qué hace?:** Interfaz de usuario responsive de carga ultrarrápida diseñada para maximizar las Core Web Vitals y asegurar indexación inmediata.
*   **🔑 Componentes Clave:**
    *   Arquitectura: Servidor Nuxt 3 con Server-Side Rendering (SSR) e Hybrid Rendering.
    *   UI/UX: Grid reactivo fluido asimétrico (estilo Pinterest) usando estrictamente unidades relativas (`rem`, `em`).
    *   SEO de Imágenes: Integración nativa de la etiqueta `<picture>` con atributos dinámicos `srcset` (`WebP` / `AVIF`).
    *   Optimización Ingress: Compresión Gzip/Brotli activa en Nginx y caché agresivo para estáticos.
*   **💡 Nota de Diseño:** Se evita cualquier renderizado puramente en el cliente (SPA) para garantizar que Googlebot indexe el 100% del texto y las imágenes semánticas sin retrasos.

### 🔹 FASE 5: El Pipeline de Analítica y Big Data (Kafka + Carga)
*   **🛠️ ¿Qué hace?:** Capa de telemetría masiva para analizar el comportamiento del usuario sin penalizar el rendimiento del servidor HTTP.
*   **🔑 Componentes Clave:**
    *   Streaming: Cluster ligero de Apache Kafka (o Redpanda) + Zookeeper en contenedores Docker.
    *   Simulador de Carga: Scripts concurrentes en Python (`asyncio`) que inyectan ráfagas de clics, heatmaps y scrolls.
    *   Consumidores Asíncronos: Workers en Python procesando las métricas en tiempo real.
*   **💡 Nota de Diseño:** El tráfico analítico corre por un canal completamente paralelo a la base de datos relacional operativa para evitar bloqueos en el hilo principal.

---

# 📊 [FLUJO LOGÍSICO INTER-CONECTADO]

```text
 FASE 1: Docker/DB/Nginx  ───►  FASE 2: FastAPI/LangGraph  ───►  FASE 4: Nuxt 3 SSR
         │                                   ▲                             │
         ▼ (Persistencia de Leads)           │ (Evaluación de Intención)   ▼ (Navegación)
 FASE 3: n8n / WhatsApp CRM ─────────────────┘                      FASE 5: Kafka Stream