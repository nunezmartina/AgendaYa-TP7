// Configuración de ESLint (TP7 - verificación de buenas prácticas en el pipeline)
import js from '@eslint/js';
import globals from 'globals';
import cypress from 'eslint-plugin-cypress';

export default [
  {
    ignores: ['node_modules/**', 'dist/**', 'coverage/**'],
  },
  js.configs.recommended,
  {
    // Lógica de negocio, tests unitarios, configuración y scripts (Node.js / CommonJS)
    files: ['src/**/*.js', 'scripts/**/*.js', '*.config.js'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'commonjs',
      globals: { ...globals.node, ...globals.jest },
    },
  },
  {
    // Tests unitarios: Node + Jest, y navegador para los tests con entorno jsdom
    files: ['tests/**/*.js'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'commonjs',
      globals: { ...globals.node, ...globals.jest, ...globals.browser },
    },
  },
  {
    // Frontend (se ejecuta en el navegador)
    files: ['frontend/**/*.js'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'script',
      globals: { ...globals.browser },
    },
  },
  {
    // Tests E2E de Cypress
    files: ['cypress/**/*.js'],
    ...cypress.configs.recommended,
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'commonjs',
      globals: { ...globals.browser, ...globals.mocha, cy: 'readonly', Cypress: 'readonly' },
    },
  },
  {
    rules: {
      'no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      eqeqeq: 'error',
      'no-var': 'error',
      'prefer-const': 'error',
    },
  },
];
