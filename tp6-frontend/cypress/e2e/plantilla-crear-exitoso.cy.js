// Responsable: Aguiar Josefina
// Flujo: Configurar plantilla de email — caso exitoso (happy path)
// Cubre: M06-R04F (ALTA), US-M06-004 Escenario 1

describe('AgendaYA - M06 Plantillas de Email', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('crea la primera plantilla del tipo y queda marcada como por defecto', () => {
    // Arrange: preparar el estado inicial — ir a la pestaña de plantillas
    cy.get('[data-cy="tab-plantillas"]').click();

    cy.get('[data-cy="nombre-input"]').type('Confirmación formal');
    cy.get('[data-cy="tipo-select"]').select('confirmacion');
    cy.get('[data-cy="asunto-input"]').type('Tu reserva con Dr. Garcia está confirmada');
    cy.get('[data-cy="saludo-input"]').type('Hola Josefina, gracias por reservar.');
    cy.get('[data-cy="cuerpo-input"]').type('Por favor llegá 5 minutos antes de tu turno.');
    cy.get('[data-cy="firma-input"]').type('Dr. García — Medicina General');
    // No se activa el tick: es la primera plantilla del tipo, debe quedar por defecto igual

    // Act: ejecutar la acción principal
    cy.get('[data-cy="guardar-plantilla-btn"]').click();

    // Assert: verificar el resultado esperado
    cy.get('[data-cy="plantilla-creada-confirmacion"]').should('be.visible');
    cy.get('[data-cy="lista-plantillas"]')
      .find('[data-cy="plantilla-item"]')
      .should('have.length', 1)
      .and('contain.text', '★')
      .and('contain.text', 'Confirmación formal');
  });
});
