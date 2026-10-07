<script setup lang="ts">
import type { ArtworkSEOResponse } from '~/types/artwork'

const route = useRoute()
const config = useRuntimeConfig()

const { data: artworkPayload, error } = await useFetch<ArtworkSEOResponse>(
  () => `/api/artworks/${route.params.slug}`,
  {
    key: `artwork-detail-${route.params.slug}`
  }
)

if (error.value || !artworkPayload.value?.data) {
  throw createError({
    statusCode: 404,
    statusMessage: 'La obra solicitada no existe o no está publicada.',
    fatal: true
  })
}

const artwork = computed(() => artworkPayload.value!.data)
const jsonLd = computed(() => artworkPayload.value!.json_ld)

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
      children: computed(() => JSON.stringify(jsonLd.value))
    }
  ]
})
</script>

<template>
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <!-- Botón para volver atrás -->
    <div class="mb-8">
      <NuxtLink to="/" class="text-sm font-medium text-gallery-muted hover:text-gallery-text transition-colors">
        ← Volver a la galería
      </NuxtLink>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-start">
      <!-- Columna de la Imagen -->
      <div class="bg-gray-100 overflow-hidden shadow-sm border border-gallery-border relative">
        <NuxtImg
          :src="`${config.public.mediaBase}/${artwork.image_base_path}.webp`"
          :alt="artwork.alt_text"
          class="w-full h-auto object-cover"
          priority
        />
        <div
          v-if="artwork.status !== 'DISPONIBLE'"
          class="absolute top-4 right-4 bg-black/75 text-white text-xs px-3 py-1.5 uppercase tracking-wider"
        >
          {{ artwork.status === 'RESERVADO' ? 'Reservado' : 'Colección Privada' }}
        </div>
      </div>

      <!-- Columna de Información y Detalles -->
      <div class="flex flex-col justify-between">
        <div>
          <h1 class="text-3xl sm:text-4xl font-serif text-gallery-text mb-4">
            {{ artwork.title }}
          </h1>
          
          <p v-if="artwork.price" class="text-2xl font-medium text-gallery-text mb-6">
            {{ artwork.price }} €
          </p>

          <div class="border-t border-b border-gallery-border py-6 my-6 space-y-3 text-sm text-gallery-muted">
            <p v-if="artwork.width_cm && artwork.height_cm">
              <strong class="text-gallery-text">Dimensiones:</strong> {{ artwork.width_cm }} x {{ artwork.height_cm }} cm
            </p>
            <p v-if="artwork.technique">
              <strong class="text-gallery-text">Técnica:</strong> {{ artwork.technique }}
            </p>
            <p v-if="artwork.year">
              <strong class="text-gallery-text">Año:</strong> {{ artwork.year }}
            </p>
          </div>

          <div class="prose prose-stone max-w-none text-gallery-muted mb-8">
            <p>{{ artwork.description || artwork.alt_text }}</p>
          </div>
        </div>

        <!-- Botón de acción / contacto -->
        <div v-if="artwork.status === 'DISPONIBLE'" class="mt-6">
          <a
            href="#contacto"
            class="w-full block text-center bg-gallery-text text-white py-3 px-6 hover:bg-gallery-muted transition-colors uppercase tracking-wider text-sm font-medium"
          >
            Consultar sobre esta obra
          </a>
        </div>
      </div>
    </div>
  </main>
</template>