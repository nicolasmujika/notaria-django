/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",   // TODAS tus plantillas
    "./core/**/*.py",          // si generas clases desde strings en Python
    "./paginas/**/*.py"
  ],
  theme: { extend: {} },
  plugins: [],
  safelist: [
    // por si acaso, evita purga de clases clave del menú
    'hidden', 'block', 'md:block', 'absolute', 'md:absolute',
    'border', 'border-slate-200', 'bg-white', 'text-gray-800'
  ]
}
