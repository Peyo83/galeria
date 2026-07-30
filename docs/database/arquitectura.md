### 📋 [FICHA GLOBAL]

* **Propósito Principal:** Establecer la arquitectura integral, desacoplada y reactiva en 5 fases de la galería de arte online. Orquesta desde la persistencia relacional (`PostgreSQL`) y la capa cognitiva de negocio (`FastAPI` + `LangChain`), pasando por pipelines de automatización (`n8n`) y renderizado ultra-rápido optimizado para SEO (`Nuxt 3 SSR`), hasta la analítica masiva en tiempo real (`Apache Kafka`).
* **Dependencias / Orden de Ejecución:** Orquestación incremental dirigida por el archivo matriz `docker-compose.yml`. Fase 1 es mandatoria (Data e Infraestructura Base). Las fases subsecuentes expanden la topología de red virtual `galeria_network_global` incorporando microservicios asíncronos distribuidos.
* **Volumen:** 5 Fases evolutivas acopladas a una jerarquía estricta de 5 directorios raíz, gobernados por un solo `docker-compose.yml` y un ecosistema unificado de variables `.env`.

---

### 🗺️ [MAPA DE COMPONENTES]

| Módulo / Servicio | Capa de la Arquitectura | Dependencia Crítica | Métrica / Foco SEO & Técnico |
| --- | --- | --- | --- |
| **`infrastructure/postgres`** | Persistencia de Datos | Docker Engine | Índices B-Tree en `slug` para SSR instantáneo. |
| **`backend/app`** | Lógica Asíncrona e IA | `postgres` (Healthcheck) | Formateo nativo JSON-LD (`VisualArtwork`). |
| **`automation`** | Workflow & CRM | `backend`, Red Virtual | Captura Webhook e integraciones n8n/WhatsApp. |
| **`frontend`** | UI/UX & Servidor SSR | `backend` REST API | Core Web Vitals (LCP < 2.5s, CLS 0), `<picture>` fluido. |
| **`infrastructure/kafka`** | Ingesta de Telemetría | `galeria_network_global` | Procesamiento concurrente de clicks y scrolling. |

---

### 🧱 [BLOQUES SECUENCIALES]

#### --- [ BLOQUE 1: Fase 1 - El Corazón y el Entorno (Docker & DB) ] ---

* 🛠️ **¿Qué hace?:** Levanta la capa física de datos relacionales y restringe los estados comerciales y de memoria del sistema de forma segura.
* 🔑 **Estructura Clave:** Contenedor `postgres:15-alpine` alimentado por el volumen con nombre `galeria_postgres_data` y mapeado al puerto `1234` en local.


* 💡 **Nota de Diseño:** Configura un `healthcheck` robusto usando `pg_isready` y optimiza las directivas de memoria interna (`shared_buffers=256MB`, `effective_cache_size=768MB`) para acelerar las lecturas de los crawlers de búsqueda. Almacena de forma nativa los campos `alt_text` y `image_base_path` para la indexación óptima en Google Imágenes.



#### --- [ BLOQUE 2: Fase 2 - El Backend y la IA (FastAPI & LangChain) ] ---

* 🛠️ **¿Qué hace?:** Provee el runtime asíncrono para despachar el catálogo de arte y ejecuta el agente cognitivo de asistencia comercial.
* 🔑 **Estructura Clave:** FastAPI + SQLAlchemy (`AsyncSession`). Orquestado con la directiva `depends_on: postgres (service_healthy)`. Inyecta de forma segura los secretos `OPENAI_API_KEY` y `GEMINI_API_KEY` desde la raíz.


* 💡 **Nota de Diseño:** Los endpoints de catálogo exponen estructuradamente payloads serializados que cumplen de manera exacta con el formato de metadatos Schema.org (`VisualArtwork`). El agente guarda memoria a través del buffer en formato `JSONB` dentro de `ai_chat_sessions`.

#### --- [ BLOQUE 3: Fase 3 - El Puente de Automatización (n8n & WhatsApp) ] ---

* 🛠️ **¿Qué hace?:** Captura las interacciones en canales de mensajería externa, procesa intenciones mediante webhooks y alerta a los administradores humanos del negocio.
* 🔑 **Estructura Clave:** Contenedor de n8n desacoplado en el subdirectorio `./automation` e interconectado nativamente a la red privada `galeria_network_global`.


* 💡 **Nota de Diseño:** Cuando el agente de IA de FastAPI detecta una clara transición de compra, el trigger modifica la tabla `purchase_leads` a `PENDIENTE_CONTACTO`. n8n escucha este evento mediante Pooling/Webhooks y dispara una alerta inmediata a canales corporativos con los metadatos de contacto cargados.

#### --- [ BLOQUE 4: Fase 4 - Rompiendo el Cuello de Botella Frontend (Nuxt 3 SSR) ] ---

* 🛠️ **¿Qué hace?:** Resuelve el problema de indexación del JavaScript tradicional, sirviendo layouts HTML semánticos e imágenes optimizadas en milisegundos.
* 🔑 **Estructura Clave:** Entorno en `./frontend` ejecutando **Nuxt 3 con Server-Side Rendering (SSR)** y tipado estricto en TypeScript.
* 💡 **Nota de Diseño:** Se implementa un layout de rejilla reactivo fluido (Pinterest style) que renderiza imágenes a través de etiquetas semánticas `<picture>` implementando `srcset` automáticos. Transforma formatos pesados sobre la marcha a variantes modernas `WebP/AVIF`, minimizando las métricas críticas del LCP (Largest Contentful Paint) y asegurando que los Meta Tags (Open Graph) sean inyectados directamente en el servidor.

#### --- [ BLOQUE 5: Fase 5 - El Pipeline de Big Data (Kafka + Generador de Carga) ] ---

* 🛠️ **¿Qué hace?:** Ingiere flujos masivos e ininterrumpidos de interacciones de usuario (clicks, scrollings, heatmaps) analizando patrones de conversión sin saturar la API del backend.
* 🔑 **Estructura Clave:** Despliegue de un clúster distribuido en `./infrastructure/kafka` mediante `docker-compose.kafka.yml` y scripts de simulación de eventos en Python concurrente.
* 💡 **Nota de Diseño:** Aísla por completo el tráfico analítico del servidor web principal. Los consumidores procesan asíncronamente las colas de streaming de datos, identificando cuáles acuarelas retienen más atención del usuario para re-inyectar pesos dinámicos de lead scoring.

---

### 📊 [DIAGRAMA LÓGICO TEXTUAL]

```text
 🪐 [FUTURO: Pipeline de Big Data (Fase 5)]       📱 [CANAL EXTERNO: WhatsApp]
    │                                                    │
    ├─► (Clicks / Telemetría / Stream)                   ▼ (Mensaje Entrante)
    │   ┌─────────────────────────────┐         ┌─────────────────────────────┐
    │   │  Cluster Apache Kafka (5)   │         │     n8n Webhook / CRM (3)   │
    │   └─────────────────────────────┘         └──────────────┬──────────────┘
    │                                                          │
    ▼ (Lecturas de Datos Analíticos)                           ▼ (Petición HTTP Asíncrona)
 ┌────────────────────────────────────────────────────────────────────────────────────────────┐
 │                                   galeria_network_global                                   │
 │                                                                                            │
 │  ┌─────────────────────────┐             ┌─────────────────────────┐                       │
 │  │      Nuxt 3 (4)         │ ──(REST)──► │      FastAPI (2)        │                       │
 │  │   [Server-Side Render]  │             │   [Agente Cognitivo]    │                       │
 │  └─────────────────────────┘             └────────────┬────────────┘                       │
 │       ▲                                               │                                    │
 │       │ (Rutas SEO Indexables)                        │ (SQLAlchemy AsyncSession)          │
 │       │                                               ▼                                    │
 │  ┌────┴────────────────────────────────────────────────────────────────────────────┐      │
 │  │                         Motor Persistente PostgreSQL (1)                        │      │
 │  ├─────────────────────────────────────────────────────────────────────────────────┤      │
 │  │  • categories / watercolors              • ai_chat_sessions / purchase_leads   │      │
 │  │  • Índices B-Tree en Slugs               • Estructuras JSONB de Memoria        │      │
 │  └─────────────────────────────────────────────────────────────────────────────────┘      │
 └────────────────────────────────────────────────────────────────────────────────────────────┘
                                                                 ▲
                                                                 │
                                                   [Volumen: galeria_postgres_data]

```