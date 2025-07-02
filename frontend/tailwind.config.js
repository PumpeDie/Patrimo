/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#0a0a0a',
        card: '#1a1a1a',
        border: '#2a2a2a',
        primary: '#3b82f6',
        muted: '#6b7280',
        accent: '#10b981',
        destructive: '#ef4444'
      },
    },
  },
  plugins: [],
}