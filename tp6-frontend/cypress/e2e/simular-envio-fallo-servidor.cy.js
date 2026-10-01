// Responsable: Lee Maria Luz
// Flujo: Simular envío de notificación — error por estado del sistema (fallo del servicio de correo)
// Cubre: M06-R01F Escenario 3 (fallo en el servicio de envío)

describe('AgendaYA - M06 Simular envío de notificación', () => {
  beforeEach(() => {
    cy.visit('/')
    cy.get('[data-cy="tab-simular"]').click()
  })

  it('muestra el error de envío fallido cuando se simula una caída del servidor', () => {
    // Arrange: preparar el estado inicial
    cy.get('[data-cy="tipo-notificacion-select"]').select('cancelacion')
    cy.get('[data-cy="email-destinatario-input"]').type('pedro@email.com')
    cy.get('[data-cy="simular-fallo-checkbox"]').check()

    // Act: ejecutar la acción principal
    cy.get('[data-cy="enviar-notificacion-btn"]').click()

    // Assert: verificar el resultado esperado
    cy.get('[data-cy="error-envio-fallido"]').should('be.visible')
    cy.get('[data-cy="notificacion-enviada-confirmacion"]').should('not.be.visible')
    cy.get('[data-cy="historial-envios"]')
      .find('[data-cy="historial-item"]')
      .should('have.length', 1)
      .and('contain.text', 'fallido')
  })
})
