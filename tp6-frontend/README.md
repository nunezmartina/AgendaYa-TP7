# AgendaYA — TP6 Testing Automatizado
### Módulo M06 — Notificaciones y Comunicaciones — Grupo N°9

Este repositorio contiene el entregable del TP N°6 de la cátedra Ingeniería y
Calidad de Software (4to año, 2026): un frontend mínimo del módulo M06,
tests E2E con Cypress y tests unitarios con Jest.

## Estructura del repositorio

```
agendaya-tp6/
├── frontend/          # Frontend mínimo (HTML + CSS + JS vanilla)
│   ├── index.html
│   ├── style.css
│   └── app.js
├── cypress/
│   └── e2e/            # Tests E2E (Tarea B)
├── tests/
│   └── logica-negocio.test.js   # Tests unitarios (Tarea C)
├── src/
│   └── logica-negocio.js        # Código fuente mínimo testeado unitariamente
├── cypress.config.js
├── package.json
└── README.md
```

## Requisitos previos

- Node.js 18 o superior
- npm

## Instalación

```bash
npm install
```

## 1. Levantar el frontend

El frontend es HTML/CSS/JS vanilla sin build step. Se recomienda servirlo con
`live-server` (incluido como script) para tener recarga automática:

```bash
npm start
```

Esto levanta el frontend en `http://localhost:5500`. Si preferís usar la
extensión **Live Server** de VS Code, el puerto por defecto también es 5500
y no hace falta cambiar nada. Si usás otro puerto, actualizá `baseUrl` en
`cypress.config.js`.

Alternativa sin instalar nada: abrir `frontend/index.html` directamente en
el navegador (protocolo `file://`) — en ese caso, ajustar `baseUrl` en
`cypress.config.js` a la ruta local del archivo o quitarlo y usar
`cy.visit('../frontend/index.html')` en los tests.

## 2. Correr los tests unitarios (Jest)

```bash
npm test
```

Esto ejecuta `tests/logica-negocio.test.js` contra `src/logica-negocio.js`.
Salida esperada: **40 tests, 40 passed** — 5 tests por cada uno de los 8
integrantes del equipo (ver evidencia completa y distribución por
integrante en el informe, sección Tarea C).

## 3. Correr los tests E2E (Cypress)

Con el frontend ya levantado (`npm start` en otra terminal):

```bash
npm run cypress:open   # modo interactivo (recomendado para ver la ejecución)
# o
npm run cypress:run    # modo headless, ideal para capturas/CI
```

Los tests están en `cypress/e2e/` y cubren ambos flujos obligatorios del
módulo M06 — **8 tests en total, uno por cada integrante del equipo**:

| Archivo | Responsable | Flujo | Variante |
|---|---|---|---|
| `plantilla-crear-exitoso.cy.js` | Aguiar Josefina | Configurar plantilla | Happy path |
| `plantilla-nombre-duplicado.cy.js` | Tejada Rocío | Configurar plantilla | Error de datos inválidos |
| `plantilla-campo-vacio.cy.js` | Nuñez Martina | Configurar plantilla | Error de campo vacío |
| `plantilla-tick-por-defecto-desplaza.cy.js` | Perez Juliana | Configurar plantilla | Happy path (variante) |
| `simular-envio-exitoso.cy.js` | Bataller Paulina | Simular envío | Happy path |
| `simular-envio-email-invalido.cy.js` | Santibañez Lucia | Simular envío | Error de datos inválidos |
| `simular-envio-fallo-servidor.cy.js` | Lee Maria Luz | Simular envío | Error de estado del sistema |
| `simular-envio-multiple-historial.cy.js` | Sanchez Ignacio | Simular envío | Happy path (variante) |

## Notas

- No hay backend real: los datos (plantillas creadas, historial de envíos)
  se guardan en memoria del navegador y se pierden al recargar la página,
  según lo permitido por la consigna del TP6 (sección 5.1).
- Todos los elementos interactivos tienen atributo `data-cy` para que los
  selectores de Cypress no dependan de clases CSS ni de texto visible.
- Si otro integrante del equipo clona el repositorio y, siguiendo estos
  pasos, no logra levantar el frontend ni correr ambas suites de test
