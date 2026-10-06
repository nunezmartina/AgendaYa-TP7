// Responsable: equipo de guardia del hotfix (Aguiar Josefina · Sanchez Ignacio)
// INC-0612 · Test de regresión E2E
// Flujo: Configurar plantilla de email — marcar una plantilla por defecto no debe
// quitar la ★ a las plantillas por defecto de otros tipos de notificación.
// Cubre: M06-R04F (ALTA, lógica del tick "por defecto"), US-M06-004 Escenario 3

describe('AgendaYA - M06 Plantillas de Email · INC-0612', () => {
  beforeEach(() => {
    cy.visit('/');
    cy.get('[data-cy="tab-plantillas"]').click();
  });

  function guardarPlantilla({ nombre, tipo, marcarPorDefecto }) {
    cy.get('[data-cy="nombre-input"]').clear();
    cy.get('[data-cy="nombre-input"]').type(nombre);
    cy.get('[data-cy="tipo-select"]').select(tipo);
    cy.get('[data-cy="asunto-input"]').clear();
    cy.get('[data-cy="asunto-input"]').type(`Asunto de ${nombre}`);
    cy.get('[data-cy="saludo-input"]').clear();
    cy.get('[data-cy="saludo-input"]').type('Hola María');
    cy.get('[data-cy="cuerpo-input"]').clear();
    cy.get('[data-cy="cuerpo-input"]').type('Te esperamos.');
    cy.get('[data-cy="firma-input"]').clear();
    cy.get('[data-cy="firma-input"]').type('Dr. García — Medicina General');
    if (marcarPorDefecto) cy.get('[data-cy="por-defecto-checkbox"]').check();
    cy.get('[data-cy="guardar-plantilla-btn"]').click();
  }

  it('crear una por defecto de cancelación conserva la ★ de la plantilla de confirmación', () => {
    // Arrange: la primera plantilla de confirmación queda por defecto
    guardarPlantilla({
      nombre: 'Confirmación formal',
      tipo: 'confirmacion',
      marcarPorDefecto: false,
    });
    cy.get('[data-cy="lista-plantillas"]')
      .contains('[data-cy="plantilla-item"]', 'Confirmación formal')
      .should('contain.text', '★');

    // Act: crear una plantilla de cancelación marcada como por defecto
    guardarPlantilla({
      nombre: 'Cancelación con motivo',
      tipo: 'cancelacion',
      marcarPorDefecto: true,
    });

    // Assert: las dos conservan la ★, cada una en su tipo
    cy.get('[data-cy="lista-plantillas"]')
      .find('[data-cy="plantilla-item"]')
      .should('have.length', 2);
    cy.get('[data-cy="lista-plantillas"]')
      .contains('[data-cy="plantilla-item"]', 'Cancelación con motivo')
      .should('contain.text', '★');
    cy.get('[data-cy="lista-plantillas"]')
      .contains('[data-cy="plantilla-item"]', 'Confirmación formal')
      .should('contain.text', '★');
  });
});
