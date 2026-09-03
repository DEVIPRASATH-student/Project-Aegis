/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        aegis: {
          white: '#FFFFFF',
          offwhite: '#F7F7F5',
          black: '#111111',
          charcoal: '#1A1A1A',
          gray: '#666666',
          border: '#E5E5E5',
          lightgray: '#F0F0EE',
          midgray: '#999999',
        },
        risk: {
          high: '#CC2936',
          medium: '#D4760A',
          low: '#1B7A3D',
        },
        status: {
          success: '#1B7A3D',
          reversed: '#CC2936',
          escrow: '#D4760A',
          pending: '#666666',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      fontSize: {
        '2xs': '0.625rem',
      },
    },
  },
  plugins: [],
}
