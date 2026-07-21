# CONFIGURACIÓN TÉCNICA DEFINITIVA: PROYECTO GALERÍA DE ARTE

## 🎯 OBJETIVOS CORE
1. Estética Visual: Minimalista, limpia, enfocada en resaltar la pintura (acuarela).
2. Rendimiento Extremo: Lazy loading nativo, optimización de Critical Rendering Path, compresión y distribución eficiente de imágenes (WebP/AVIF).
3. SEO Técnico por Defecto: Marcado estructurado Schema.org dinámico (VisualArtwork y ArtGallery), SSR para indexación instantánea, URLs semánticas amigables e indexabilidad estricta en Google Imágenes.

---

## 🗺️ HOJA DE RUTA REESTRUCTURADA (5 FASES)

### Fase 1: El Corazón y el Entorno (Docker & DB Optimizado)
*   **Infraestructura:** Stack aislado en Docker (`postgres:15-alpine`) con volumen persistente y variables de entorno dinámicas.
*   **Modelo de Datos:** PostgreSQL. Tablas normalizadas para `categories` y `watercolors`, extendidas para SEO técnico (campos `slug` indexados únicos y metadatos `alt_text`).
*   **Persistencia de Negocio:** Tablas `ai_chat_sessions` y `purchase_leads` para soportar la retención de estados conversacionales y la detección automatizada de intenciones de compra.

### Fase 2: El Backend y la IA (FastAPI & LangChain)
*   **Arquitectura:** API asíncrona construida en FastAPI utilizando SQLAlchemy/SQLModel (AsyncSession).
*   **Optimización SEO:** Endpoints preparados para inyectar payloads estructurados directamente en formato Schema.org JSON-LD desde el servidor.
*   **Capa de IA:** Integración de agentes inteligentes usando LangChain con persistencia en la tabla `ai_chat_sessions` para detectar transiciones hacia la intención de compra.

### Fase 3: El Puente de Automatización (n8n & WhatsApp)
*   **Orquestación:** Despliegue contenerizado de n8n dentro de la misma red global de Docker (`galeria_network_global`).
*   **Flujo de Trabajo:** Webhook para captura de mensajes entrantes de WhatsApp, reenvío al Agente de FastAPI para su procesamiento, y trigger de alertas humanas en canales dedicados cuando el lead pase a estado `PENDIENTE_CONTACTO`.

### Fase 4: Rompiendo el Cuello de Botella Frontend (Nuxt 3 + TypeScript)
*   **Arquitectura:** Migración de SPA pura a **Nuxt 3 (Server-Side Rendering / Hybrid Rendering)** con TypeScript para solventar el retraso de indexación del JavaScript en cliente.
*   **UI/UX:** Grid reactivo fluido (Layout estilo Pinterest) implementado con unidades relativas (`rem`, `em`) y diseño completamente fluido.
*   **SEO de Imágenes:** Uso estricto de componentes adaptativos (`<picture>`, `srcset`, formatos modernos WebP/AVIF) gestionados nativamente para optimizar los Core Web Vitals (LCP y CLS).
*   **Analítica:** Integración limpia del DataLayer para Google Tag Manager y GA4.

### Fase 5: El Pipeline de Big Data (Kafka + Generador de Carga)
*   **Infraestructura de Streaming:** Cluster distribuido de Apache Kafka desplegado bajo contenedores Docker en la arquitectura de red interna.
*   **Simulación de Carga:** Scripts de Python concurrentes para inyectar telemetría y eventos de clics/navegación masiva, y consumidores asíncronos que procesen el streaming de comportamiento web en tiempo real.