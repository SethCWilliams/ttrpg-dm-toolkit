/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        gray: {
          750: '#374151',
          850: '#1f2937'
        }
      }
    },
  },
  plugins: [],
}