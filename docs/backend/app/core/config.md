# 📋 [FICHA GLOBAL]

* **Propósito Principal:** Mapear y tipar fuertemente las variables de entorno atómicas del sistema operativo a través de un Singleton inmutable de Pydantic, abstrayendo la lógica de construcción de credenciales de red mediante una propiedad computada en memoria dinámica.
* **Dependencias / Orden de Ejecución:** Archivo inicial. Es el primer módulo importado en el ciclo de vida del backend. Es consumido de manera obligatoria por `backend/app/core/database.py` para levantar el pool de sockets del motor de persistencia.
* **Volumen:** Inicializa 1 clase de esquema de configuración (`Settings`) y expone 1 Singleton global instanciado (`settings`).

---

# 🧱 [BLOQUES SECUENCIALES]

#### --- [ BLOQUE 1: Declaración de Propiedades Estáticas e Ingesta ] ---

* 🛠️ **¿Qué hace?:** Define los campos obligatorios del entorno que la aplicación requiere para funcionar, forzando la validación de tipos durante el arranque del proceso de FastAPI.
* 🔑 **Estructura Clave:** Tipado estricto (`str`, `int`), decorador `model_config` configurado con `extra="ignore"` para omitir variables residuales del sistema operativo.
* 💡 **Nota de Diseño:** Al utilizar `BaseSettings`, si falta una sola variable atómica en el entorno (`POSTGRES_USER`, etc.), el proceso de Python fallará inmediatamente arrojando un `ValidationError` en el startup, impidiendo despliegues corruptos en el contenedor Docker.

#### --- [ BLOQUE 2: Generador de String de Conexión Dinámico (`DATABASE_URL`) ] ---

* 🛠️ **¿Qué hace?:** Ensambla en caliente la URI con el esquema asíncrono `postgresql+asyncpg` evaluando de forma inteligente si la petición se origina dentro de la red del orquestador Docker o en el host local.
* 🔑 **Estructura Clave:** Decorador `@computed_field`, propiedad de solo lectura `@property`, constructor robusto `PostgresDsn.build`.
* 💡 **Nota de Diseño:** Resuelve elegantemente el problema de inconsistencia del host y puerto: si el entorno inyecta el puerto interno mapeado (`5432`), asume la comunicación nativa de la red bridge de Docker apuntando al contenedor `postgres`. Si se modifica para pruebas locales aisladas, ajusta el target de red de forma transparente.

---

# 📊 [DIAGRAMA LÓGICO TEXTUAL]

```text
 ⚙️ [ .env: Variables Atómicas ] ──► [ Ingesta / Validación BaseSettings ]
                                                     │
                                           (Procesamiento Interno)
                                                     ▼
 [ core/database.py ] ◄─── (Importación) ─── [ settings.DATABASE_URL (Computed) ]

```
