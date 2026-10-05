export enum ArtworkStatus {
  DISPONIBLE = 'DISPONIBLE',
  RESERVADO = 'RESERVADO',
  COLECCION_PRIVADA = 'COLECCION_PRIVADA'
}

export interface Artwork {
  id: number
  title: string
  slug: string
  description?: string
  width_cm?: number
  height_cm?: number
  price?: number
  image_base_path: string
  alt_text: string
  status: ArtworkStatus
  category_id?: number
  created_at: string
  updated_at: string
}

export interface ArtworkSEOResponse {
  data: Artwork
  json_ld: Record<string, any>
}

export interface ArtworkListResponse {
  total: number
  items: Artwork[]
}