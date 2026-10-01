// Responsable: Tejada Rocío
// Flujo: Configurar plantilla de email — error por datos inválidos (nombre duplicado)
// Cubre: M06-R04F (ALTA), US-M06-004 Escenario 4

describe('AgendaYA - M06 Plantillas de Email', () => {
  beforeEach(() => {
    cy.visit('/')
    cy.get('[data-cy="tab-plantillas"]').click()
  })

  function completarFormularioPlantilla(nombre) {
    cy.get('[data-cy="nombre-input"]').clear().type(nombre)
    cy.get('[data-cy="tipo-select"]').select('cancelacion')
    cy.get('[data-cy="asunto-input"]').clear().type('Tu turno fue cancelado')
    cy.get('[data-cy="saludo-input"]').clear().type('Hola Rocio')
    cy.get('[data-cy="cuerpo-input"]').clear().type('Lamentamos informarte la cancelación.')
    cy.get('[data-cy="firma-input"]').clear().type('Dr. García')
  }

  it('no permite guardar una plantilla con un nombre ya existente', () => {
    // Arrange: preparar el estado inicial — crear una primera plantilla válida
    completarFormularioPlantilla('Cancelación estándar')
    cy.get('[data-cy="guardar-plantilla-btn"]').click()
    cy.get('[data-cy="plantilla-creada-confirmacion"]').should('be.visible')

    // Act: intentar crear una segunda plantilla con el mismo nombre
    completarFormularioPlantilla('Cancelación estándar')
    cy.get('[data-cy="guardar-plantilla-btn"]').click()

    // Assert: verificar el resultado esperado
    cy.get('[data-cy="error-nombre-duplicado"]').should('be.visible')
    cy.get('[data-cy="lista-plantillas"]')
      .find('[data-cy="plantilla-item"]')
      .should('have.length', 1) // la segunda no se guardó
  })
})
