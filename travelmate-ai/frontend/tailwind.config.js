/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'system-ui', '-apple-system', '"Segoe UI"', 'sans-serif'],
      },
      // One brand palette for the whole app: Royal Indigo + Sunset Saffron (+ emerald for money/success)
      colors: {
        primary: '#1e1b4b',    // Royal Indigo
        secondary: '#f97316',  // Sunset Saffron
        tertiary: '#059669',   // Emerald - costs, success
        surface: '#faf8ff',
        surfaceDim: '#d2d9f4',
        onSurface: '#131b2e',
        outline: '#787680',
      },
      boxShadow: {
        glass: '0 4px 20px -2px rgba(15, 23, 42, 0.04), 0 2px 6px -1px rgba(15, 23, 42, 0.02)',
        glow: '0 10px 25px -4px rgba(249, 115, 22, 0.25)',
        float: '0 20px 40px -12px rgba(30, 27, 75, 0.35)',
      },
    },
  },
  plugins: [],
};
