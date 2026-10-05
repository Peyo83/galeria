export default defineNuxtConfig({
  devtools: { enabled: false },

  modules: [
    '@nuxt/image',
    '@pinia/nuxt',
    '@nuxtjs/tailwindcss'
  ],

  image: {
    domains: ['localhost', 'backend', '127.0.0.1'],
    alias: {
      media: process.env.NUXT_PUBLIC_MEDIA_BASE || 'http://localhost:8000/media'
    },
    format: ['webp', 'jpg'],
    quality: 85
  },

  routeRules: {
    '/': { ssr: true },
    '/obra/**': { ssr: true },
    '/sobre-mi': { ssr: true, prerender: true },
    '/admin/**': { ssr: false }
  },

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1',
      mediaBase: process.env.NUXT_PUBLIC_MEDIA_BASE || 'http://localhost:8000/media'
    }
  }
})