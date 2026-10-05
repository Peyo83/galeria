<script setup lang="ts">
import type { ArtworkSEOResponse } from '~/types/artwork'

const route = useRoute()
const config = useRuntimeConfig()
const slug = computed(() => route.params.slug as string)

// Data fetching en servidor con re-evaluación reactiva según la ruta
const { data: artworkPayload, error } = await useFetch<ArtworkSEOResponse>(
  `/artworks/${slug.value}`,
  {
    baseURL: config.public.apiBase,
    key: `artwork-detail-${slug.value}`
  }
)

// Manejo de errores SSR determinista para Googlebot (404 estricto)
if (error.value || !artworkPayload.value?.data) {
  throw createError({
    statusCode: 404,
    statusMessage: 'La obra solicitada no existe o no está publicada.',
    fatal: true
  })
}

const artwork = computed(() => artworkPayload.value!.data)
const jsonLd = computed(() => artworkPayload.value!.json_ld)

// Inyección de SEO Semántico (OpenGraph, Twitter Cards, Schema.org)
useHead({
  title: `${artwork.value.title} | Acuarela Original`,
  meta: [
    { name: 'description', content: artwork.value.description || artwork.value.alt_text },
    { property: 'og:type', content: 'article' },
    { property: 'og:title', content: artwork.value.title },
    { property: 'og:description', content: artwork.value.description || artwork.value.alt_text },
    { property: 'og:image', content: `${config.public.mediaBase}/${artwork.value.image_base_path}.webp` },
    { name: 'twitter:card', content: 'summary_large_image' }
  ],
  script: [
    {
      type: 'application/ld+json',
      // Se garantiza el escape correcto de caracteres UTF-8 sin deshidratación
      children: computed(() => JSON.stringify(jsonLd.value))
    }
  ]
})
</script>

<template>
  <main class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <nav aria-label="Navegación secundaria" class="mb-8">
      <NuxtLink 
        to="/" 
        class="inline-flex items-center text-sm text-gallery-muted hover:text-gallery-text transition-colors"
      >
        ← Volver a la Galería
      </NuxtLink>
    </nav>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
      <!-- Visualizador de la obra con NuxtImg (Optimizado) -->
      <div class="lg:col-span-7 bg-gallery-card border border-gallery-border p-4 rounded-sm">
        <NuxtImg
          :src="`${artwork.image_base_path}.webp`"
          :alt="artwork.alt_text"
          provider="none"
          sizes="sm:100vw md:50vw lg:700px"
          format="webp"
          quality="85"
          loading="eager"
          fetchpriority="high"
          class="w-full h-auto object-contain max-h-[80vh] mx-auto"
        />
      </div>

      <!-- Ficha Técnica y Metadatos de la Obra -->
      <section class="lg:col-span-5 space-y-6">
        <header class="border-b border-gallery-border pb-4">
          <h1 class="text-3xl sm:text-4xl font-serif text-gallery-text mb-2 tracking-tight">
            {{ artwork.title }}
          </h1>
          <p class="text-xs uppercase tracking-widest text-gallery-muted font-mono">
            Técnica: Acuarela sobre papel
          </p>
        </header>

        <div class="space-y-3 text-sm text-gallery-text">
          <div v-if="artwork.width_cm && artwork.height_cm" class="flex justify-between py-1 border-b border-gallery-border/40">
            <span class="text-gallery-muted">Dimensiones</span>
            <span class="font-medium">{{ artwork.width_cm }} × {{ artwork.height_cm }} cm</span>
          </div>

          <div class="flex justify-between py-1 border-b border-gallery-border/40">
            <span class="text-gallery-muted">Disponibilidad</span>
            <span class="font-medium capitalize">{{ artwork.status }}</span>
          </div>

          <div v-if="artwork.price" class="flex justify-between text-base font-semibold pt-2 text-gallery-text">
            <span>Precio</span>
            <span>{{ artwork.price }} €</span>
          </div>
        </div>

        <div v-if="artwork.description" class="prose text-gallery-text/80 text-sm leading-relaxed pt-2">
          <p>{{ artwork.description }}</p>
        </div>
      </section>
    </div>
  </main>
</template>