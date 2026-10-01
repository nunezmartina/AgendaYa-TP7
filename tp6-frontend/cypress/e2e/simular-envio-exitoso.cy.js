// Responsable: Bataller Paulina
// Flujo: Simular envío de notificación — caso exitoso (happy path)
// Cubre: M06-R01F, US-M06-001 Escenario 1

describe('AgendaYA - M06 Simular envío de notificación', () => {
  beforeEach(() => {
    cy.visit('/')
    cy.get('[data-cy="tab-simular"]').click()
  })

  it('simula el envío de un email de confirmación a un email válido', () => {
    // Arrange: preparar el estado inicial
    cy.get('[data-cy="tipo-notificacion-select"]').select('confirmacion')
    cy.get('[data-cy="email-destinatario-input"]').type('maria@email.com')
    // el checkbox de "simular fallo" queda sin marcar

    // Act: ejecutar la acción principal
    cy.get('[data-cy="enviar-notificacion-btn"]').click()

    // Assert: verificar el resultado esperado
    cy.get('[data-cy="notificacion-enviada-confirmacion"]').should('be.visible')
    cy.get('[data-cy="historial-envios"]')
      .find('[data-cy="historial-item"]')
      .should('have.length', 1)
      .and('contain.text', 'maria@email.com')
      .and('contain.text', 'enviado')
  })
})
