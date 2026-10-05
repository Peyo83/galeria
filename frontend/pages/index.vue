<script setup lang="ts">
import type { ArtworkListResponse } from '~/types/artwork'

const config = useRuntimeConfig()

// SSR Fetch hacia FastAPI
const { data: artworksData, pending, error } = await useFetch<ArtworkListResponse>(
  `${config.public.apiBase}/artworks`,
  {
    lazy: false,
    server: true
  }
)

// Inyección SEO Schema.org ArtGallery
useHead({
  title: 'Catálogo de Acuarelas Originales',
  meta: [
    { name: 'description', content: 'Galería de arte online especializada en acuarelas originales. Colecciones exclusivas y obras disponibles.' }
  ],
  script: [
    {
      type: 'application/ld+json',
      children: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'ArtGallery',
        'name': 'Galería de Acuarelas',
        'url': 'https://tu-dominio-galeria.com',
        'description': 'Exposición y catálogo de obras en acuarela hechas a mano.'
      })
    }
  ]
})
</script>

<template>
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <header class="text-center mb-16">
      <h1 class="text-4xl sm:text-5xl font-serif text-gallery-text tracking-wide mb-4">
        Colección de Acuarelas
      </h1>
      <p class="text-gallery-muted max-w-2xl mx-auto text-lg">
        Explora las obras originales. Cada pieza es una manifestación única de luz, pigmento y agua.
      </p>
    </header>

    <div v-if="pending" class="text-center py-20">
      <p class="text-gallery-muted font-serif animate-pulse">Cargando galería...</p>
    </div>

    <div v-else-if="error" class="text-center py-20 text-red-600">
      <p>Error al cargar las obras de arte. Inténtelo más tarde.</p>
    </div>

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 sm:gap-12">
      <article
        v-for="art in artworksData?.items"
        :key="art.id"
        class="group bg-gallery-card border border-gallery-border overflow-hidden transition-all duration-300 hover:shadow-lg"
      >
        <NuxtLink :to="`/obra/${art.slug}`" class="block">
          <div class="aspect-4/3 bg-gray-100 overflow-hidden relative">
            <NuxtImg
              :src="`${config.public.mediaBase}/${art.image_base_path}_thumb.webp`"
              :alt="art.alt_text"
              loading="lazy"
              class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            />
            <div
              v-if="art.status !== 'DISPONIBLE'"
              class="absolute top-3 right-3 bg-black/75 text-white text-xs px-2.5 py-1 uppercase tracking-wider"
            >
              {{ art.status === 'RESERVADO' ? 'Reservado' : 'Colección Privada' }}
            </div>
          </div>
          
          <div class="p-6">
            <h2 class="text-xl font-serif text-gallery-text mb-2 group-hover:text-gallery-muted transition-colors">
              {{ art.title }}
            </h2>
            <div class="flex justify-between items-center text-sm text-gallery-muted mt-4 pt-4 border-t border-gallery-border">
              <span v-if="art.width_cm && art.height_cm">{{ art.width_cm }} x {{ art.height_cm }} cm</span>
              <span v-if="art.price" class="font-medium text-gallery-text">{{ art.price }} €</span>
            </div>
          </div>
        </NuxtLink>
      </article>
    </div>
  </main>
</template>