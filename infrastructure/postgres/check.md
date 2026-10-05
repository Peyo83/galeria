### Guía de Verificación y Diagnóstico del Contenedor PostgreSQL (`galeria_db`)

Esta documentación recoge la batería de comandos de inspección y validación del esquema de base de datos para la **Versión 1**. Garantiza que la capa de persistencia esté correctamente aprovisionada antes de conectar el backend FastAPI.

---

### 1. Estado de Salud del Contenedor (*Healthcheck*)

* **Objetivo:** Verificar que el contenedor de PostgreSQL está en ejecución, que el proceso principal responde y que el *healthcheck* definido en `docker-compose.yml` (`pg_isready`) devuelve un estado positivo.
* **Comando:**
```bash
docker inspect --format='{{json .State.Health.Status}}' galeria_db

```


* **Respuesta esperada:**
```json
"healthy"

```



---

### 2. Inspección de Tablas Creadas (`\dt`)

* **Objetivo:** Confirmar que el script `init.sql` ha ejecutado DDL correctamente al inicializar el volumen y que las tres tablas core de la v1 (`users`, `categories`, `watercolors`) existen en el esquema público (`public`).
* **Comando:**
```bash
docker exec -it galeria_db psql -U galeria_admin -d galeria_db -c "\dt"

```


* **Respuesta esperada:**
```text
           List of relations
 Schema |    Name     | Type  |     Owner     
--------+-------------+-------+---------------
 public | categories  | table | galeria_admin
 public | users       | table | galeria_admin
 public | watercolors | table | galeria_admin
(3 rows)

```



---

### 3. Validación del Tipo Enumerado Nativo (`artwork_status`)

* **Objetivo:** Comprobar que el tipo personalizado de PostgreSQL (`ENUM`) está registrado con las tres etiquetas exactas requeridas para la gestión de disponibilidad en la galería (`DISPONIBLE`, `RESERVADO`, `COLECCION_PRIVADA`).
* **Comando:**
```bash
docker exec -it galeria_db psql -U galeria_admin -d galeria_db -c "\dT+"

```


* **Respuesta esperada:**
```text
                                                List of data types
 Schema |      Name      | Internal name | Size | Elements |  Owner  | Access privileges | Description 
--------+----------------+---------------+------+----------+---------+-------------------+-------------
 public | artwork_status | artwork_status| var  | DISPONIBLE        | galeria_admin |                   | 
        |                |               |      | RESERVADO         |               |                   | 
        |                |               |      | COLECCION_PRIVADA |               |                   | 

```



---

### 4. Diagnóstico de Estructura e Índices B-Tree (`\d watercolors`)

* **Objetivo:** Verificar las columnas, los tipos de datos de la tabla principal `watercolors`, la Foreign Key hacia `categories` y, especialmente, la presencia de:
1. El índice B-Tree único automático sobre `slug` (`watercolors_slug_key`).
2. El índice explícito sobre el Enum `status` (`idx_watercolors_status`).
3. El índice explícito sobre la FK `category_id` (`idx_watercolors_category_id`).


* **Comando:**
```bash
docker exec -it galeria_db psql -U galeria_admin -d galeria_db -c "\d watercolors"

```


* **Respuesta esperada:**
```text
                                              Table "public.watercolors"
     Column      |           Type           | Collation | Nullable |                     Default                      
-----------------+--------------------------+-----------+----------+--------------------------------------------------
 id              | integer                  |           | not null | nextval('watercolors_id_seq'::regclass)
 title           | character varying(255)   |           | not null | 
 slug            | character varying(280)   |           | not null | 
 description     | text                     |           |          | 
 width_cm        | numeric(5,2)             |           |          | 
 height_cm       | numeric(5,2)             |           |          | 
 price           | numeric(10,2)            |           |          | 
 image_base_path | character varying(512)   |           | not null | 
 alt_text        | character varying(255)   |           | not null | 
 status          | artwork_status           |           |          | 'DISPONIBLE'::artwork_status
 category_id     | integer                  |           |          | 
 created_at      | timestamp with time zone |           |          | CURRENT_TIMESTAMP
 updated_at      | timestamp with time zone |           |          | CURRENT_TIMESTAMP
Indexes:
    "watercolors_pkey" PRIMARY KEY, btree (id)
    "watercolors_slug_key" UNIQUE CONSTRAINT, btree (slug)
    "idx_watercolors_category_id" btree (category_id)
    "idx_watercolors_status" btree (status)
Foreign-key constraints:
    "watercolors_category_id_fkey" FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
Triggers:
    update_watercolors_updated_at BEFORE UPDATE ON watercolors FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()

```



---

### 5. Verificación del Trigger de Automatización de Metadatos

* **Objetivo:** Inspeccionar el catálogo del sistema (`information_schema.triggers`) para confirmar que la función PL/pgSQL `update_updated_at_column()` está correctamente vinculada al evento `BEFORE UPDATE` de la tabla `watercolors`.
* **Comando:**
```bash
docker exec -it galeria_db psql -U galeria_admin -d galeria_db -c "
SELECT trigger_name, event_manipulation, action_statement 
FROM information_schema.triggers 
WHERE event_object_table = 'watercolors';"

```


* **Respuesta esperada:**
```text
         trigger_name          | event_manipulation |            action_statement            
-------------------------------+--------------------+----------------------------------------
 update_watercolors_updated_at | UPDATE             | EXECUTE FUNCTION update_updated_at_column()
(1 row)

```



---

### 6. Comprobación de Base de Datos Vacía (*Zero-Data Check*)

* **Objetivo:** Confirmar que no existen datos semilla en ninguna de las tablas tras la limpieza del script `init.sql`, garantizando que la inserción de categorías, usuarios y obras arrancará limpia vía Swagger / FastAPI.
* **Comando:**
```bash
docker exec -it galeria_db psql -U galeria_admin -d galeria_db -c "
SELECT 
  (SELECT count(*) FROM users) AS total_users,
  (SELECT count(*) FROM categories) AS total_categories,
  (SELECT count(*) FROM watercolors) AS total_watercolors;
"

```


* **Respuesta esperada:**
```text
 total_users | total_categories | total_watercolors 
-------------+------------------+-------------------
           0 |                0 |                 0
(1 row)

```



---


### 7. Crear Admin

```Bash
docker exec -it galeria_backend python -m app.cli.create_admin --email admin@galeria.com --name "name"

```

(El script solicitará la contraseña de forma oculta mediante getpass).