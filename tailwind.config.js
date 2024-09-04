/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
        fontFamily: {
          Ocean: ['Oceanwide', 'sans-serif'],
          Advent: ['Advent', 'sans-serif'],
        },
        fontWeight: {
          light: 100,
          normal: 400,
          semibold: 600,
        },
    },
  },
  plugins: [],
}

