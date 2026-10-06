/**
 * @jest-environment jsdom
 *
 * INC-0612 · Test de regresión del hotfix (TP7, Grupo 9)
 * Síntoma: al guardar una plantilla que queda "por defecto", las plantillas por
 * defecto de OTROS tipos de notificación perdían la ★ y esos tipos quedaban sin
 * plantilla para enviar emails.
 * Regla (M06-R04F / US-M06-004 Esc. 3): la nueva por defecto desplaza solo a la
 * anterior de SU MISMO tipo; hay exactamente una por defecto por cada tipo.
 *
 * Carga el frontend real (index.html + app.js) en un DOM simulado y usa el
 * formulario igual que un administrador.
 */
const fs = require('fs');
const path = require('path');

const FRONTEND = path.join(__dirname, '..', 'frontend');

function cargarFrontend() {
  const html = fs.readFileSync(path.join(FRONTEND, 'index.html'), 'utf8');
  document.documentElement.innerHTML = html.replace(/<script[\s\S]*?<\/script>/g, '');
  jest.isolateModules(() => require(path.join(FRONTEND, 'app.js')));
}

function guardarPlantilla({ nombre, tipo, marcarPorDefecto }) {
  const campo = (cy) => document.querySelector(`[data-cy="${cy}"]`);
  campo('nombre-input').value = nombre;
  campo('tipo-select').value = tipo;
  campo('asunto-input').value = `Asunto de ${nombre}`;
  campo('saludo-input').value = 'Hola {nombre_invitado}';
  campo('cuerpo-input').value = 'Cuerpo del email';
  campo('firma-input').value = 'Dr. García — Medicina General';
  campo('por-defecto-checkbox').checked = marcarPorDefecto;
  document
    .getElementById('form-plantilla')
    .dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
}

function itemsDelListado() {
  return [...document.querySelectorAll('[data-cy="plantilla-item"]')].map((li) => li.textContent);
}

describe('INC-0612 — la plantilla por defecto de un tipo no afecta a los otros tipos', () => {
  beforeEach(cargarFrontend);

  test('crear una por defecto de "cancelación" conserva la ★ de "confirmación"', () => {
    // Arrange: la primera plantilla de confirmación queda por defecto automáticamente
    guardarPlantilla({
      nombre: 'Confirmación formal',
      tipo: 'confirmacion',
      marcarPorDefecto: false,
    });
    expect(itemsDelListado()).toEqual(['★ Confirmación formal — confirmacion']);

    // Act: el admin crea una plantilla de cancelación con el tick "por defecto"
    guardarPlantilla({
      nombre: 'Cancelación con motivo',
      tipo: 'cancelacion',
      marcarPorDefecto: true,
    });

    // Assert: cada tipo conserva su propia plantilla por defecto
    expect(itemsDelListado()).toEqual([
      '★ Confirmación formal — confirmacion',
      '★ Cancelación con motivo — cancelacion',
    ]);
  });

  test('con tres tipos, sigue habiendo exactamente una ★ por tipo', () => {
    guardarPlantilla({
      nombre: 'Confirmación formal',
      tipo: 'confirmacion',
      marcarPorDefecto: false,
    });
    guardarPlantilla({
      nombre: 'Recordatorio estándar',
      tipo: 'recordatorio',
      marcarPorDefecto: false,
    });
    guardarPlantilla({
      nombre: 'Confirmación breve',
      tipo: 'confirmacion',
      marcarPorDefecto: true,
    });

    const items = itemsDelListado();
    const porDefecto = items.filter((t) => t.startsWith('★'));
    expect(porDefecto).toEqual([
      '★ Recordatorio estándar — recordatorio',
      '★ Confirmación breve — confirmacion',
    ]);
    expect(items).toContain('Confirmación formal — confirmacion'); // pasó a alternativa
  });
});
