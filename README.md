A continuación se presenta el diseño y contenido técnico del archivo **`README.md`** raíz para la orquestación del proyecto. Se ha estructurado aplicando de forma estricta el formato visual modular solicitado, eliminando prosa innecesaria y actuando como un panel de control técnico interactivo para producción y desarrollo local.

---

# 📋 [FICHA GLOBAL]

* **Propósito Principal:** Repositorio centralizador de documentación arquitectónica, dependencias operativas y comandos de despliegue para la Galería de Arte en Acuarela distribuidos en un ecosistema acoplado de 5 fases.


* **Dependencias / Orden de Ejecución:** Docker Engine / Docker Compose en entorno WSL2 (Ubuntu). Requiere inicializar variables criptográficas y de red mediante inyección en Shell antes de la interacción con el CLI.


* **Volumen:** Orquesta 1 archivo `.env`, 1 `.gitignore`, 1 `docker-compose.yml`, 4 directorios independientes de microservicios y servicios de persistencia indexada.



---

# 🗺️ [MAPA DE COMPONENTES]

| Módulo del Sistema | Ubicación Física | Docker Image / Contexto | Puerto Expuesto | Rol Técnico y Crítico |
| --- | --- | --- | --- | --- |
| **Infraestructura DB** | `/infrastructure/postgres` | `postgres:15-alpine`<br> | `1234` (Local)

 | Persistencia relacional indexada por B-Tree para SSR.

 |
| **Backend Core** | `/backend` | Dockerfile personalizado

 | `8000` (Local)

 | Engine asíncrono FastAPI + LangChain (Estructuras JSON-LD).

 |
| **Automation** | `/automation` | n8n Container Instance

 | `5678` (Local) | Captura Webhook de eventos transaccionales vía WhatsApp.

 |
| **Frontend UI** | `/frontend` | Nuxt 3 (Servidor Node/Nitro)

 | `3000` (Local) | Renderizado SSR híbrido e inyección nativa de Core Web Vitals.

 |
| **Big Data Stream** | `/infrastructure/kafka` | Apache Kafka + Zookeeper

 | `9092` (Local) | Ingesta asíncrona distribuidora de telemetría y clicks de usuario.

 |

---

# 🧱 [BLOQUES SECUENCIALES]

#### --- [ BLOQUE 1: Prerrequisitos e Inicialización del Entorno ] ---

* 🛠️ **¿Qué hace?:** Prepara el entorno del Shell inyectando de forma atómica y segura las variables declaradas en el archivo `.env` raíz sin persistirlas permanentemente en el sistema operativo del host.


* 🔑 **Estructura Clave:** Comando de Bash idempotente: `export $(grep -v '^#' .env | grep -v '^$' | xargs)`.


* 💡 **Nota de Diseño:** Evita fallas catastróficas al levantar contenedores Docker que mapean puertos dinámicos (`${POSTGRES_PORT}`) o que inicializan pools de comunicación asíncrona con LLMs (OpenAI/Gemini).



#### --- [ BLOQUE 2: Despliegue de la Fase 1 (Persistencia Relacional) ] ---

* 🛠️ **¿Qué hace?:** Inicializa de forma aislada el motor relacional levantando las estructuras, tipos enums personalizados y semillas de datos (Seeders).


* 🔑 **Estructura Clave:** Directiva de arranque de infraestructura: `docker-compose up -d postgres`.


* 💡 **Nota de Diseño:** Postgres ejecuta automáticamente el script `/infrastructure/postgres/init.sql` acoplado en modo de solo lectura (`ro`). El contenedor incorpora un script de validación `healthcheck` que ejecuta `pg_isready` internamente cada 5 segundos.



#### --- [ BLOQUE 3: Compilación y Despliegue del Backend de Inteligencia Artificial ] ---

* 🛠️ **¿Qué hace?:** Compila las dependencias de Python asíncronas e integra la capa cognitiva de LangChain, enlazándose a la base de datos una vez que esta se declara saludable.


* 🔑 **Estructura Clave:** Comando `docker-compose up -d --build backend`. Dependencia interna condicionada por `service_healthy`.


* 💡 **Nota de Diseño:** FastAPI arranca su pool asíncrono (`AsyncSession`) solo cuando el canal de red relacional está validado. Provee serialización automática en Schema.org (`VisualArtwork`) para optimizar el rastreo de los bots de búsqueda.



#### --- [ BLOQUE 4: Testing y Verificación de Integridad ] ---

* 🛠️ **¿Qué hace?:** Ejecuta comandos de inspección rápidos para verificar que los índices B-Tree en campos `slug` y las tablas de memoria conversacional estén operativas.


* 🔑 **Estructura Clave:** Comandos CLI: `docker exec -it galeria_db pg_isready` y verificación de logs `docker compose logs -f backend`.


* 💡 **Nota de Diseño:** Permite auditar cuellos de botella del Critical Rendering Path en fases de desarrollo antes de inyectar las capas de UI de Nuxt 3.



---

# 📊 [DIAGRAMA LÓGICO TEXTUAL]

```text
 [⚙️ CLI Host: Inyección de .env] ────► [⚡ Docker Compose Daemon]
                                                │
       ┌────────────────────────────────────────┴────────────────────────────────────────┐
       ▼ (Fase 1: Capa de Datos)                                                         ▼ (Fase 2: Capa Lógica)
┌─────────────────────────────────┐                                             ┌─────────────────────────────────┐
│       CONTENEDOR: postgres      │                                             │       CONTENEDOR: backend       │
├─────────────────────────────────┤                                             ├─────────────────────────────────┤
│ • Init: init.sql (Montado: ro)  │                                             │ • Engine: FastAPI               │
│ • Health: pg_isready (5s)       │◄───[depends_on: service_healthy (Bloqueo)]──┤ • Memoria IA: JSONB en DB       │
│ • Índices B-Tree en Slugs (SEO) │                                             │ • Formato Schema: VisualArtwork │
└─────────────────────────────────┘                                             └─────────────────────────────────┘

```

---

### 🚀 CÓDIGO FUENTE DE PRODUCCIÓN: `README.md`

Copia el bloque inferior en la raíz de tu proyecto bajo el nombre de `README.md` para contar con la documentación viva alineada a la arquitectura global.

```markdown
# 🎨 CONFIGURACIÓN TÉCNICA DEFINITIVA: PROYECTO GALERÍA DE ARTE

Plataforma contenerizada de alto rendimiento optimizada para la exposición e indexación index-first (SEO Técnico) de portfolios pictóricos de acuarela, integrada con agentes conversacionales cognitivos y streaming analítico en tiempo real.

## ⚡ REQUISITOS DE ENTORNO DE DESARROLLO (WSL2 / UBUNTU)

Antes de invocar comandos en el Docker CLI o abrir entornos integrados de desarrollo (IDE), inyecte de manera segura las variables de entorno locales ejecutando en la terminal de Bash:
```bash
export $(grep -v '^#' .env \vert{} grep -v '^$' | xargs)

```

---

## 🎯 OBJETIVOS CORE DE LA ARQUITECTURA

1. **Estética Visual Estricta:** Diseño minimalista limpio donde la carga de los lienzos (acuarelas) domine la interfaz de usuario.
2. **Rendimiento Extremo (Web Vitals):** Lazy loading nativo, compresión agresiva de imágenes pesadas a formatos asíncronos modernos (`WebP` / `AVIF`), optimización del Critical Rendering Path para lograr LCP < 2.5s y CLS de 0 absoluto.
3. **SEO Técnico Nativo por Defecto:** Inyección estructurada en el servidor mediante datos estructurados de Schema.org (`VisualArtwork` y `ArtGallery` en formato JSON-LD), Server-Side Rendering (SSR) dinámico mediante Nuxt 3, URLs amigables limpias basadas en `slug` indexados e indexabilidad forzada para Google Imágenes usando atributos `alt_text` mandatorios.

---

## 🗺️ HOJA DE RUTA ARQUITECTÓNICA POR FASES

### 🔹 Fase 1: El Corazón y el Entorno (Docker & DB Optimizado) [FASE ACTUAL]

* **Infraestructura:** Despliegue del contenedor aislado `postgres:15-alpine` alimentado por un volumen persistente nominal controlado (`galeria_postgres_data`).
* **Modelo de Datos Avanzado:** Esquema físico relacional estructurado en `categories` y `watercolors` con soporte SEO nativo (índices B-Tree en campos `slug` únicos y columnas `alt_text` / `image_base_path`).
* **Persistencia de Estado:** Tablas dedicadas para agentes cognitivos (`ai_chat_sessions`) utilizando el tipo binario `JSONB` e intenciones de compra (`purchase_leads`).

### 🔹 Fase 2: El Backend y la IA (FastAPI & LangChain)

* **API asíncrona:** Construcción bajo el paradigma de concurrencia nativa con FastAPI y SQLAlchemy/SQLModel ejecutando `AsyncSession`.
* **Payloads Semánticos:** Endpoints especializados en inyectar metadatos JSON-LD estructurados directamente desde las respuestas del motor de backend.
* **Capa Inteligente:** Orquestación de agentes relacionales mediante LangChain, reteniendo históricos conversacionales en el storage transaccional.

### 🔹 Fase 3: El Puente de Automatización (n8n & WhatsApp)

* **Integración Operativa:** Instancia contenerizada del motor de flujos lógicos n8n comunicada internamente mediante el driver `bridge` a la red privada `galeria_network_global`.
* **Workflow Transaccional:** Webhooks reactivos para procesar strings binarios de entrada de WhatsApp, derivación automática de intenciones al backend y alertas automáticas a administradores humanos al transicionar leads a `PENDIENTE_CONTACTO`.

### 🔹 Fase 4: Rompiendo el Cuello de Botella Frontend (Nuxt 3 + TypeScript)

* **Paradigma de Renderizado:** Migración a **Nuxt 3 Server-Side Rendering (SSR) / Hybrid Rendering** con tipado fuerte TypeScript para eliminar el retardo de renderizado e indexación de crawlers (Googlebot) en SPAs tradicionales.
* **Layout Fluido:** Grid responsivo asimétrico (estilo Pinterest) basado estrictamente en unidades relativas (`rem`, `em`) sin layouts fijos bloqueantes.
* **Pipeline Web de Imágenes:** Inyección de directivas nativas HTML5 con la etiqueta `<picture>`, usando atributos dinámicos `srcset` para ajustar las densidades de pantalla al vuelo.

### 🔹 Fase 5: El Pipeline de Big Data (Kafka + Generador de Carga)

* **Ingesta Masiva:** Despliegue de un cluster distribuido de Apache Kafka para aislar el tráfico analítico del flujo HTTP operacional del sitio web.
* **Simulación e Ingesta:** Scripts concurrentes en Python simulando interacciones masivas (clicks, heatmaps, scrolls) procesados asíncronamente por consumidores analíticos.

---

## 🛠️ PANEL DE CONTROL DE INFRAESTRUCTURA (COMANDOS RÁPIDOS)

**1. Desplegar la Base de Datos con Inicialización Física Automática:**

```bash
docker compose up -d postgres

```

**2. Verificar el Estado Saludable (Healthcheck) del Motor Relacional:**

```bash
docker exec -it galeria_db pg_isready -U user -d db

```

**3. Compilar y Levantar el Backend Asíncrono de FastAPI:**

```bash
docker compose up -d --build backend

```

**4. Inspeccionar Logs del Servidor en Tiempo Real:**

```bash
docker compose logs -f backend

```

**5. Detener el Stack de Infraestructura Completo (Preservando el Volumen de Datos):**

```bash
docker compose down

```

```

```