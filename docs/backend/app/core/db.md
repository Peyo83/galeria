# 📋 [FICHA GLOBAL]

* **Propósito Principal:** Establecer el ciclo de vida y la factoría de conexiones asíncronas no bloqueantes a la base de datos PostgreSQL, optimizando la reutilización de sockets mediante un pool de conexiones para soportar alta concurrencia.
* **Dependencias / Orden de Ejecución:** Requiere la instanciación previa del objeto `settings` desde `backend/app/core/config.py`. Este extrae en caliente las variables atómicas individuales inyectadas por Docker desde el entorno global (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` y `POSTGRES_PORT` asignado al backend) para orquestar y formatear la URI de conexión asíncrona puramente en la memoria dinámica del runtime.
* **Volumen:** Inicializa 1 motor asíncrono (`engine`), 1 factoría de sesiones (`async_session_maker`) y 1 generador de dependencias inyectable (`get_db`).

---

# 🧱 [BLOQUES SECUENCIALES]

#### --- [ BLOQUE 1: Configuración del Motor Asíncrono (`engine`) ] ---

* 🛠️ **¿Qué hace?:** Crea la instancia central de conexión utilizando `create_async_engine` alimentándose de la propiedad de conexión expuesta por el módulo `config`. Define el comportamiento del pool de sockets TCP compartidos en la red interna de Docker.
* 🔑 **Estructura Clave:**
* `pool_size=20`: Mantiene 20 conexiones persistentes abiertas en memoria en caliente para mitigar el coste de handshake de CPU.
* `max_overflow=10`: Permite abrir hasta 10 conexiones adicionales bajo picos de tráfico repentinos (límite absoluto de 30).
* `pool_pre_ping=True`: Robustez operativa. Envía de forma automática un comando ligero (`SELECT 1`) antes de entregar la conexión al backend. Si el contenedor `galeria_db` se reinició o la conexión murió, la descarta de forma segura y negocia una nueva de inmediato.


* 💡 **Nota de Diseño:** Al interactuar con el driver `asyncpg` mediante `SQLModel`, se activa `future=True` para garantizar compatibilidad nativa con SQLAlchemy 2.0. `echo=False` apaga el logging masivo SQL por consola para no penalizar la I/O del contenedor en producción.

#### --- [ BLOQUE 2: La Factoría de Sesiones (`async_session_maker`) ] ---

* 🛠️ **¿Qué hace?:** Define la clase factoría preconfigurada encargada de instanciar objetos `AsyncSession` individuales cada vez que el backend necesita ejecutar una transacción transaccional.
* 🔑 **Estructura Clave:**
* `bind=engine`: Vincula de forma obligatoria las sesiones al motor asíncrono configurado en el bloque previo.
* `class_=AsyncSession`: Fuerza a la factoría a trabajar en modo asíncrono, obligando el uso de sintaxis `await` en las operaciones de I/O.
* `expire_on_commit=False`: Evita que los atributos de las entidades de Python (como slugs o textos ALT de las acuarelas) queden invalidados tras confirmar un `commit`. Vital para inyectar datos en la respuesta HTTP o pasárselos al agente de IA después de persistir cambios sin lanzar consultas secundarias imprevistas.



#### --- [ BLOQUE 3: El Inyector de Dependencias (`get_db`) ] ---

* 🛠️ **¿Qué hace?:** Actúa como el *Dependency Provider* asíncrono. Genera un canal transaccional limpio, aislado y con ámbito (scope) exclusivo para cada petición HTTP entrante.
* 🔑 **Estructura Clave:**
* `async with async_session_maker() as session:` Context Manager asíncrono. Garantiza la apertura segura y, críticamente, fuerza el cierre del socket (`close()`) al terminar de procesar la petición HTTP, devolviendo la conexión al pool de Docker de forma atómica.
* `yield session`: Entrega la sesión activa al controlador de FastAPI y pausa la ejecución del generador en ese punto exacto hasta que la petición finalice su ciclo de vida.


* 💡 **Nota de Diseño:** Al tipar el retorno como `AsyncGenerator[AsyncSession, None]`, FastAPI gestiona la limpieza de recursos de forma nativa. Si ocurre una excepción no controlada en el router, el Context Manager captura la falla y ejecuta un `rollback` automático de la transacción, previniendo estados corruptos en la base de datos relacional.

---

# 📊 [DIAGRAMA LÓGICO TEXTUAL]

```text
 ⚙️ [ Variables atómicas .env ] ──► [ Inyección Docker-Compose ] ──► [ core/config.py (String de conexión en Memoria) ]
                                                                                   │
                                                                                   ▼
 [ Petición HTTP ] ──► [ Controlador FastAPI (Depends(get_db)) ] ◄────────── [ core/database.py ]
                                    │
 ┌──────────────────────────────────┴──────────────────────────────────┐
 │ 🎰 PASO 1: get_db() invoca a async_session_maker()                  │
 │ 🎰 PASO 2: Solicita conexión válida al Pool (Pre-Ping: SELECT 1)     │
 │ 🎰 PASO 3: yield session ──► (El router procesa lógica de negocio)   │
 └──────────────────────────────────┬──────────────────────────────────┘
                                    │ (Fin de la Petición / Envío de Respuesta)
                                    ▼
 [ Sesión Cerrada Atómicamente ] ──► [ Conexión devuelta intacta al Pool ]

```