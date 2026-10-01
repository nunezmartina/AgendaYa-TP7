const { defineConfig } = require('cypress')

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:5500', // ver README: ajustar según cómo se sirva el frontend
    setupNodeEvents(on, config) {
      // no se requieren plugins adicionales para este TP
    },
  },
})
