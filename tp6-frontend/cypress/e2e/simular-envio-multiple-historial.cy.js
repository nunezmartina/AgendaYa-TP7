// Responsable: Sanchez Ignacio
// Flujo: Simular envío de notificación — caso exitoso (variante: múltiples envíos)
// Cubre: M06-R01F + M06-R05F, US-M06-009 (base del historial de notificaciones)

describe('AgendaYA - M06 Simular envío de notificación', () => {
  beforeEach(() => {
    cy.visit('/')
    cy.get('[data-cy="tab-simular"]').click()
  })

  it('acumula en el historial dos envíos exitosos de distinto tipo en la misma sesión', () => {
    // Arrange + Act: enviar una notificación de confirmación
    cy.get('[data-cy="tipo-notificacion-select"]').select('confirmacion')
    cy.get('[data-cy="email-destinatario-input"]').type('maria@email.com')
    cy.get('[data-cy="enviar-notificacion-btn"]').click()
    cy.get('[data-cy="notificacion-enviada-confirmacion"]').should('be.visible')

    // Act: enviar una segunda notificación, esta vez de cancelación, a otro invitado
    cy.get('[data-cy="tipo-notificacion-select"]').select('cancelacion')
    cy.get('[data-cy="email-destinatario-input"]').type('juan@email.com')
    cy.get('[data-cy="enviar-notificacion-btn"]').click()

    // Assert: el historial de la sesión tiene ambos envíos, en orden, con estado "enviado"
    cy.get('[data-cy="notificacion-enviada-confirmacion"]').should('be.visible')
    cy.get('[data-cy="historial-envios"]')
      .find('[data-cy="historial-item"]')
      .should('have.length', 2)
    cy.get('[data-cy="historial-envios"]').should('contain.text', 'maria@email.com')
    cy.get('[data-cy="historial-envios"]').should('contain.text', 'juan@email.com')
    cy.get('[data-cy="historial-envios"]').find('[data-cy="historial-item"]').eq(0).should('contain.text', 'enviado')
    cy.get('[data-cy="historial-envios"]').find('[data-cy="historial-item"]').eq(1).should('contain.text', 'enviado')
  })
})
