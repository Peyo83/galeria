export default defineEventHandler(async (event) => {
  try {
    const response = await $fetch('http://backend:8000/api/v1/artworks')
    // Nos aseguramos de devolver un objeto plano limpio
    return response
  } catch (error: any) {
    throw createError({
      statusCode: error.statusCode || error.response?.status || 500,
      statusMessage: 'Error al obtener las obras del backend'
    })
  }
})