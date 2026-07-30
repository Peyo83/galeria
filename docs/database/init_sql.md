### 📋 [FICHA GLOBAL]

* **Propósito Principal:** Inicialización determinista del motor de persistencia relacional PostgreSQL (`postgres:15-alpine`). Define tipos personalizados, estructura tabular optimizada para indexación SEO (Image Search & SSR) y la infraestructura de datos para agentes conversacionales de IA y lead scoring en tiempo real.
* **Dependencias / Orden de Ejecución:** Fase 1 (Infraestructura). Se ejecuta automáticamente al arrancar el contenedor a través del punto de montaje `/docker-entrypoint-initdb.d/init.sql`. Debe ejecutarse previo a la inicialización de la API en FastAPI.
* **Volumen:** Crea 1 tipo `ENUM`, 4 tablas relacionales, 3 índices de rendimiento B-Tree, 1 función PL/pgSQL con 2 triggers automáticos y 6 registros semilla para entornos locales de desarrollo.

---

### 🗺️ [MAPA DE TIPOS Y ESTRUCTURAS]

| Entidad / Tipo | Tipo de Objeto | Clave Primaria / Valores | Índices / Relaciones | Propósito Técnico |
| --- | --- | --- | --- | --- |
| **`artwork_status`** | `ENUM` | `DISPONIBLE`, `RESERVADO`, `COLECCION_PRIVADA` | N/A | Restringe la integridad del estado comercial del lienzo. |
| **`categories`** | `TABLE` | `id` (SERIAL) | `slug` (UNIQUE) | Agrupación semántica para enrutamiento SSR en Nuxt 3. |
| **`watercolors`** | `TABLE` | `id` (SERIAL) | `category_id` (FK), `slug` (UNIQUE) | Catálogo de obras de arte con soporte SEO para imágenes. |
| **`ai_chat_sessions`** | `TABLE` | `id` (SERIAL) | `session_id` (UNIQUE) | Almacenamiento JSONB persistente para la memoria analítica del Agente (LangChain). |
| **`purchase_leads`** | `TABLE` | `id` (SERIAL) | `session_id` (FK), `watercolor_id` (FK) | Cola de transiciones a leads de compra calificados para triggers en n8n. |

---

### 🧱 [BLOQUES SECUENCIALES]

#### --- [ BLOQUE 1: Tipos Enum y Configuración Inicial ] ---

* 🛠️ **¿Qué hace?:** Define de forma segura y tolerante a fallos (`IF NOT EXISTS`) el tipo de dato enumerado para gestionar los estados comerciales de cada obra de arte sin sobrecargar strings en la base de datos.
* 🔑 **Estructura Clave:** Tipo `artwork_status` con tres estados finitos (`DISPONIBLE`, `RESERVADO`, `COLECCION_PRIVADA`).
* 💡 **Nota de Diseño:** Envolver la validación dentro de un bloque anónimo `DO $$` previene excepciones en despliegues concurrentes o reinicios del contenedor local.

#### --- [ BLOQUE 2: Estructura de Tablas (Maestras y Catálogo) ] ---

* 🛠️ **¿Qué hace?:** Genera los esquemas relacionales para la taxonomía (`categories`) y las entidades del porfolio pictórico (`watercolors`).
* 🔑 **Estructura Clave:**
* `categories.slug` y `watercolors.slug`: Campos indexed únicos para resoluciones de rutas amigables estructuradas.
* `watercolors.image_base_path`: Almacena el path agnóstico de resolución para inyectar payloads adaptativos (`srcset`, AVIF/WebP) en Nuxt 3.
* `watercolors.alt_text`: Campo nativo obligatorio diseñado para poblar la directiva HTML `alt` garantizando la indexación orgánica en Google Imágenes.


* 💡 **Nota de Diseño:** El borrado de categorías está configurado como `ON DELETE SET NULL`, previniendo que la eliminación de una colección borre en cascada las acuarelas asociadas, las cuales simplemente pasarán a un estado huérfano temporal.

#### --- [ BLOQUE 3: Persistencia de Negocio e Inteligencia Artificial ] ---

* 🛠️ **¿Qué hace?:** Provee la persistencia necesaria para la capa de IA conversacional y la captura automatizada de intenciones transaccionales.
* 🔑 **Estructura Clave:**
* `ai_chat_sessions.chat_history`: Tipo de datos `JSONB` indexable para lecturas y escrituras asíncronas de la memoria del buffer del agente LangChain.
* `purchase_leads`: Relaciona la sesión de chat con el cuadro de interés a través de llaves foráneas indexadas, inicializando el lead en `PENDIENTE_CONTACTO`.


* 💡 **Nota de Diseño:** Las foreign keys hacia estas tablas implementan `ON DELETE CASCADE`. Si una sesión de chat es purgada del sistema, sus intenciones de compra huérfanas se eliminan atómicamente, manteniendo la base de datos limpia.

#### --- [ BLOQUE 4: Optimización de Rendimiento (Índices) ] ---

* 🛠️ **¿Qué hace?:** Inyecta índices B-Tree específicos en la base de datos para optimizar las consultas del servidor.
* 🔑 **Estructura Clave:** Índices en `categories(slug)`, `watercolors(slug)` y `watercolors(status)`.
* 💡 **Nota de Diseño:** Crucial para mitigar cuellos de botella durante el renderizado por el lado del servidor (SSR) en Nuxt 3. Evita Scans completos de tabla (`Seq Scan`) transformándolos en búsquedas indexadas de alta velocidad (`Index Scan`) cuando el router busca una obra o colecciones disponibles.

#### --- [ BLOQUE 5: Automatización de Metadatos (Triggers) ] ---

* 🛠️ **¿Qué hace?:** Automatiza la actualización del campo `updated_at` cada vez que un registro en las tablas críticas sufre una modificación.
* 🔑 **Estructura Clave:** Función PL/pgSQL `update_updated_at_column()` disparada `BEFORE UPDATE`.
* 💡 **Nota de Diseño:** Garantiza la consistencia interna sin delegar la responsabilidad al backend (FastAPI), permitiendo un control preciso de marcas temporales útil para cabeceras HTTP de caché (`Last-Modified`) y sitemaps dinámicos.

#### --- [ BLOQUE 6: Semillas de Datos (Seeders) ] ---

* 🛠️ **¿Qué hace?:** Realiza la carga inicial de datos tipificados en el entorno local para habilitar pruebas funcionales de renderizado de forma inmediata.
* 🔑 **Estructura Clave:** Cláusula `ON CONFLICT (slug) DO NOTHING` basada en restricciones únicas.
* 💡 **Nota de Diseño:** Permite que los scripts de infraestructura e integración continua (`CI/CD`) sean completamente idempotentes. El script puede correr N veces sin duplicar información ni romper restricciones de clave única.

---

### 📊 [DIAGRAMA LÓGICO TEXTUAL]

```text
 [⚙️ Inicialización: Tipo ENUM artwork_status]
                     │
                     ▼
             ┌───────────────┐
             │  categories   │
             └───────────────┘
                     │ (1)
                     │
                     │ (N) ON DELETE SET NULL
                     ▼
             ┌───────────────┐
             │  watercolors  │ ◄───────┐
             └───────────────┘         │
                     ▲                 │ (N) ON DELETE CASCADE
                     │                 │
                     │ (N)             │
    ┌────────────────┴────────────────┐│
    │         purchase_leads          ││
    └────────────────┬────────────────┘│
                     │ (N)             │
                     │                 │
                     │ (1)             │
                     ▼                 │
    ┌─────────────────────────────────┐│
    │        ai_chat_sessions         │├─[⚡ Índices Críticos (B-Tree Slugs)]
    └─────────────────────────────────┘│
                     ▲                 ├─[⚙️ Triggers: update_updated_at]
                     │                 │
                     └─────────────────┴─[🌱 Seeders: Datos Iniciales Idempotentes]

```