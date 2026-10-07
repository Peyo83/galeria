export default defineEventHandler(async (event) => {
  const slug = event.context.params?.slug

  try {
    const response = await $fetch(`http://backend:8000/api/v1/artworks/${slug}`)
    return response
  } catch (error: any) {
    const status = error.statusCode || error.response?.status || 404
    throw createError({
      statusCode: status,
      statusMessage: 'Obra no encontrada en el backend'
    })
  }
})