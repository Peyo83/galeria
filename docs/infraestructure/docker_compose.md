### 📋 [FICHA GLOBAL]

* **Propósito Principal:** Orquestación determinista y declarativa del entorno contenerizado local de desarrollo. Administra el ciclo de vida del motor de persistencia relacional (`PostgreSQL`) optimizado para búsquedas SEO, y el servidor asíncrono cognitivo (`FastAPI`), encapsulándolos en una red aislada y asegurando un orden de arranque estrictamente secuencial mediante *healthchecks*.


* **Dependencias / Orden de Ejecución:** Fase 1 (Infraestructura). Requiere la inyección previa en el Shell de las variables declaradas en el archivo `.env` raíz. El nodo `postgres` debe alcanzar el estado *healthy* antes de iniciar la compilación y despliegue del nodo `backend`.


* **Volumen:** Crea 2 servicios (`postgres`, `backend`), 1 volumen nominal persistente (`galeria_postgres_data`), y 1 red virtual interna con driver bridge (`galeria_network_global`).



---

### 🗺️ [MAPA DE COMPONENTES]

| Servicio | Imagen / Contexto de Compilación | Puertos (Host:Container) | Dependencias de Arranque | Propósito Crítico en la Arquitectura |
| --- | --- | --- | --- | --- |
| **`postgres`** | `postgres:15-alpine`<br> | `${POSTGRES_PORT}:5432`<br> | Ninguna | Almacenamiento relacional. Ejecuta el DDL de inicialización optimizado para indexación de imágenes y SSR.

 |
| **`backend`** | Contexto: `./backend` (Dockerfile)

 | `8000:8000`<br> | `postgres` (`service_healthy`)

 | API asíncrona FastAPI. Despacha metadatos estructurados Schema.org JSON-LD y gestiona la memoria de la IA.

 |

---

### 🧱 [BLOQUES SECUENCIALES]

#### --- [ BLOQUE 1: Configuración de Servicios (Servicio `postgres`) ] ---

* 🛠️ **¿Qué hace?:** Levanta la instancia de base de datos relacional PostgreSQL basada en una distribución Alpine Linux ligera, montando los scripts de inicialización de tablas e índices del sistema.


* 🔑 **Estructura Clave:**
* Volumen de inicialización: `./infrastructure/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro` (Modo Solo Lectura).


* Control de salud (`healthcheck`): Evalúa cada 5 segundos mediante `pg_isready` el estado del servicio utilizando credenciales inyectadas.




* 💡 **Nota de Diseño:** Sobrescribe el comando por defecto (`command: postgres ...`) para optimizar el consumo de recursos a nivel de kernel de base de datos (`shared_buffers=256MB`, `effective_cache_size=768MB`), lo que acelera los tiempos de respuesta de consultas complejas de enrutamiento SEO o búsquedas del backend.



#### --- [ BLOQUE 2: Configuración de Servicios (Servicio `backend`) ] ---

* 🛠️ **¿Qué hace?:** Orquesta la compilación e inicio del servidor de lógica de negocio y procesamiento de lenguaje natural.


* 🔑 **Estructura Clave:**
* Directiva `build`: Define el path `./backend` y busca su respectivo `Dockerfile` para la creación de la imagen local.


* Directiva `depends_on`: Aplica un bloqueo secuencial explícito condicionado a que `postgres` devuelva estado saludable.




* 💡 **Nota de Diseño:** Al configurar el puerto interno del pool de conexiones del backend fijado estricto a `POSTGRES_PORT=5432`, se abstrae al backend del puerto aleatorio expuesto en la máquina host anfitriona (`${POSTGRES_PORT}`), permitiendo cambiar el puerto del host en el `.env` sin romper la comunicación interna de la red virtual.



#### --- [ BLOQUE 3: Recursos Globales (Persistencia de Red y Volúmenes) ] ---

* 🛠️ **¿Qué hace?:** Define los recursos compartidos independientes a los que se acoplan los contenedores para la comunicación interna y el almacenamiento no volátil.


* 🔑 **Estructura Clave:**
* Volumen: `postgres_data` mapeado al controlador nativo con nombre exclusivo `galeria_postgres_data`.


* Red: `galeria_network_global` inicializada explícitamente con el driver de aislamiento lógico `bridge`.




* 💡 **Nota de Diseño:** Encapsular los componentes dentro de una red con nombre estricto garantiza que las fases futuras (como el módulo de automatización n8n de Fase 3 o el cluster distribuido Apache Kafka de Fase 5) puedan integrarse dinámicamente al mismo espacio de direccionamiento IP sin interrumpir los servicios activos.



---

### 📊 [DIAGRAMA LÓGICO TEXTUAL]

```text
 ⚙️ [Variables del Entorno: .env Host] ──────────┐
                                                 ▼
                                     ┌───────────────────────┐
                                     │  docker-compose.yml   │
                                     └───────────┬───────────┘
                                                 │
                  ┌──────────────────────────────┴──────────────────────────────┐
                  ▼                                                             ▼
┌───────────────────────────────────────────────┐               ┌───────────────────────────────────────────────┐
│              SERVICIO: postgres               │               │               SERVICIO: backend               │
├───────────────────────────────────────────────┤               ├───────────────────────────────────────────────┤
│ • Imagen: postgres:15-alpine                  │               │ • Build Context: ./backend                    │
│ • Docker Healthcheck: pg_isready (Cada 5s)    │               │ • Env Injected: OpenAI / Gemini / Postgres Key │
│ • Puerto Expuesto Host: ${POSTGRES_PORT}      │               │ • Puerto Expuesto Host: 8000:8000             │
└───────────────────────┬───────────────────────┘               └───────────────────────┬───────────────────────┘
                        │                                                               │
                        │                                                               │
                        ▼ (Aislamiento de Tráfico Lógico y Almacenamiento Seguro)       │
    ===================  galeria_network_global [Driver: bridge] ====================◄──┘
                        ▲
                        │ (Punto de Montaje de Volumen Persistente)
                        ▼
             [galeria_postgres_data]

```