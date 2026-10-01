// Responsable: Santibañez Lucia
// Flujo: Simular envío de notificación — error por datos inválidos (formato de email)
// Cubre: M06-R01F, US-M06-001 Escenario 2

describe('AgendaYA - M06 Simular envío de notificación', () => {
  beforeEach(() => {
    cy.visit('/')
    cy.get('[data-cy="tab-simular"]').click()
  })

  it('no envía la notificación si el email tiene formato inválido', () => {
    // Arrange: preparar el estado inicial
    cy.get('[data-cy="tipo-notificacion-select"]').select('confirmacion')
    cy.get('[data-cy="email-destinatario-input"]').type('usuario@')

    // Act: ejecutar la acción principal
    cy.get('[data-cy="enviar-notificacion-btn"]').click()

    // Assert: verificar el resultado esperado
    cy.get('[data-cy="error-email-invalido"]').should('be.visible')
    cy.get('[data-cy="notificacion-enviada-confirmacion"]').should('not.be.visible')
    cy.get('[data-cy="historial-envios"]').find('[data-cy="historial-item"]').should('have.length', 0)
  })
})
