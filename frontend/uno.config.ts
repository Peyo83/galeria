import {
  defineConfig,
  presetUno,
  presetAttributify,
  presetIcons,
  presetTypography
} from 'unocss'

export default defineConfig({
  presets: [
    presetUno(),
    presetAttributify(),
    presetIcons(),
    presetTypography()
  ],
  theme: {
    colors: {
      gallery: {
        bg: '#fbfbfb',
        card: '#ffffff',
        border: '#e5e5e5',
        text: '#171717',
        muted: '#737373'
      }
    }
  }
})