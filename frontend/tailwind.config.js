/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        peach: {
          DEFAULT: '#FFDBBB',
          light: '#FFF2E6',
          dark: '#E6C4A5'
        },
        stone: {
          DEFAULT: '#CCBEB1',
          light: '#E2D9D0',
          dark: '#B0A193'
        },
        taupe: {
          DEFAULT: '#997E67',
          light: '#B29780',
          dark: '#7D6450'
        },
        brown: {
          DEFAULT: '#664930',
          light: '#805E40',
          dark: '#4D3622'
        },
        canvas: '#FAF8F5',
        surface: '#FFFFFF',
        appText: {
          DEFAULT: '#26221F',
          muted: '#75685D',
          subtle: '#9E9085'
        },
        appBorder: {
          DEFAULT: '#E6DDD4',
          subtle: '#F0EAE3',
          dark: '#D5C9BE'
        },
        allowed: {
          DEFAULT: '#16A34A',
          soft: '#DCFCE7',
          border: '#86EFAC'
        },
        blocked: {
          DEFAULT: '#DC2626',
          soft: '#FEE2E2',
          border: '#FCA5A5'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace']
      }
    },
  },
  plugins: [],
}
