// Responsable: Perez Juliana
// Flujo: Configurar plantilla de email — caso exitoso (variante del happy path)
// Cubre: M06-R04F (ALTA, lógica del tick "por defecto"), US-M06-004 Escenario 3

describe('AgendaYA - M06 Plantillas de Email', () => {
  beforeEach(() => {
    cy.visit('/');
    cy.get('[data-cy="tab-plantillas"]').click();
  });

  function completarFormularioPlantilla({ nombre, tipo, marcarPorDefecto }) {
    cy.get('[data-cy="nombre-input"]').clear();
    cy.get('[data-cy="nombre-input"]').type(nombre);
    cy.get('[data-cy="tipo-select"]').select(tipo);
    cy.get('[data-cy="asunto-input"]').clear();
    cy.get('[data-cy="asunto-input"]').type('Tu turno con {nombre_profesional} fue cancelado', {
      parseSpecialCharSequences: false,
    });
    cy.get('[data-cy="saludo-input"]').clear();
    cy.get('[data-cy="saludo-input"]').type('Hola Juliana');
    cy.get('[data-cy="cuerpo-input"]').clear();
    cy.get('[data-cy="cuerpo-input"]').type('Lamentamos informarte la cancelación de tu turno.');
    cy.get('[data-cy="firma-input"]').clear();
    cy.get('[data-cy="firma-input"]').type('Dr. García — Medicina General');
    if (marcarPorDefecto) {
      cy.get('[data-cy="por-defecto-checkbox"]').check();
    }
  }

  it('una nueva plantilla con el tick activado desplaza a la anterior por defecto', () => {
    // Arrange: preparar el estado inicial — crear la primera plantilla del tipo
    // "cancelacion" (queda por defecto automáticamente al ser la única)
    completarFormularioPlantilla({
      nombre: 'Cancelación breve',
      tipo: 'cancelacion',
      marcarPorDefecto: false,
    });
    cy.get('[data-cy="guardar-plantilla-btn"]').click();
    cy.get('[data-cy="lista-plantillas"]')
      .find('[data-cy="plantilla-item"]')
      .should('have.length', 1)
      .and('contain.text', '★ Cancelación breve');

    // Act: crear una segunda plantilla del mismo tipo, con el tick activado
    completarFormularioPlantilla({
      nombre: 'Cancelación con motivo',
      tipo: 'cancelacion',
      marcarPorDefecto: true,
    });
    cy.get('[data-cy="guardar-plantilla-btn"]').click();

    // Assert: la nueva queda como por defecto y la anterior pierde la estrella
    cy.get('[data-cy="lista-plantillas"]')
      .find('[data-cy="plantilla-item"]')
      .should('have.length', 2);
    cy.get('[data-cy="lista-plantillas"]')
      .contains('[data-cy="plantilla-item"]', 'Cancelación con motivo')
      .should('contain.text', '★');
    cy.get('[data-cy="lista-plantillas"]')
      .contains('[data-cy="plantilla-item"]', 'Cancelación breve')
      .should('not.contain.text', '★');
  });
});
