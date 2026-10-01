// Responsable: Nuñez Martina
// Flujo: Configurar plantilla de email — error por datos inválidos (campo obligatorio vacío)
// Cubre: criterio de aceptación 5.4 del TP6 ("formularios validan campo vacío")

describe('AgendaYA - M06 Plantillas de Email', () => {
  beforeEach(() => {
    cy.visit('/')
    cy.get('[data-cy="tab-plantillas"]').click()
  })

  it('muestra error si se intenta guardar dejando el cuerpo del email vacío', () => {
    // Arrange: preparar el estado inicial — completar todo menos el cuerpo
    cy.get('[data-cy="nombre-input"]').type('Recordatorio incompleto')
    cy.get('[data-cy="tipo-select"]').select('recordatorio')
    cy.get('[data-cy="asunto-input"]').type('Recordatorio: tu turno es mañana')
    cy.get('[data-cy="saludo-input"]').type('Hola Martina')
    // cuerpo-input queda vacío a propósito
    cy.get('[data-cy="firma-input"]').type('Dr. García')

    // Act: ejecutar la acción principal
    cy.get('[data-cy="guardar-plantilla-btn"]').click()

    // Assert: verificar el resultado esperado
    cy.get('[data-cy="error-campo-vacio"]').should('be.visible')
    cy.get('[data-cy="plantilla-creada-confirmacion"]').should('not.be.visible')
    cy.get('[data-cy="lista-plantillas"]').find('[data-cy="plantilla-item"]').should('have.length', 0)
  })
})
