/**
 * AgendaYA — Tests unitarios del módulo M06 (Notificaciones)
 * Tarea C del TP6. 40 tests en total: cada uno de los 8 integrantes del
 * equipo desarrolló 5 tests, cubriendo al menos 2 funciones/comportamientos
 * distintos con casos normales, límite/borde y de error, según exige la
 * sección 7.1 de la consigna. Asistidos con IA (ver prompts documentados
 * en el informe, sección Tarea C).
 */

const {
  esEmailValido,
  generarAsunto,
  calcularEsPorDefecto,
  puedeQuitarPorDefecto,
  construirCuerpoEmail,
  puedeEliminarPlantilla,
  esElegibleParaRecordatorio,
  validarCamposPlantilla,
  enmascararEmail,
} = require('../src/logica-negocio');

// ============================================================================
// Responsable: Nuñez Martina
// Funciones: esEmailValido (3 tests) + generarAsunto (2 tests)
// ============================================================================
describe('Nuñez Martina — esEmailValido y generarAsunto', () => {
  test('[esEmailValido] caso normal: email con formato correcto retorna true', () => {
    expect(esEmailValido('usuario@dominio.com')).toBe(true);
  });

  test('[esEmailValido] caso de error: falta el dominio (usuario@) retorna false', () => {
    expect(esEmailValido('usuario@')).toBe(false);
  });

  test('[esEmailValido] caso borde: string vacío retorna false', () => {
    expect(esEmailValido('')).toBe(false);
  });

  test('[generarAsunto] caso normal: asunto de confirmación sigue el patrón exacto', () => {
    expect(generarAsunto('confirmacion', { nombreProfesional: 'Dr. García' }))
      .toBe('Tu reserva con Dr. García está confirmada');
  });

  test('[generarAsunto] caso normal: asunto de recordatorio sigue el patrón exacto', () => {
    expect(generarAsunto('recordatorio', { nombreProfesional: 'Dr. García' }))
      .toBe('Recordatorio: tu turno con Dr. García es mañana');
  });
});
// ============================================================================
// Responsable: Aguiar Josefina
// Funciones: calcularEsPorDefecto (3 tests) + puedeQuitarPorDefecto (2 tests)
// ============================================================================
describe('Aguiar Josefina — calcularEsPorDefecto y puedeQuitarPorDefecto', () => {
  test('[calcularEsPorDefecto] caso normal: primera plantilla del tipo queda por defecto aunque el tick esté apagado', () => {
    expect(calcularEsPorDefecto({ existeOtraPlantillaDelTipo: false, tickActivado: false })).toBe(true);
  });

  test('[calcularEsPorDefecto] caso normal: nueva plantilla con tick activado desplaza a la anterior', () => {
    expect(calcularEsPorDefecto({ existeOtraPlantillaDelTipo: true, tickActivado: true })).toBe(true);
  });

  test('[calcularEsPorDefecto] caso normal: nueva plantilla sin tick activado queda como alternativa', () => {
    expect(calcularEsPorDefecto({ existeOtraPlantillaDelTipo: true, tickActivado: false })).toBe(false);
  });

  test('[puedeQuitarPorDefecto] caso de error: no se puede quitar el tick si es la única plantilla del tipo', () => {
    expect(puedeQuitarPorDefecto({ esUnicaPlantillaDelTipo: true })).toBe(false);
  });

  test('[puedeQuitarPorDefecto] caso normal: se puede quitar el tick si existe otra plantilla del tipo', () => {
    expect(puedeQuitarPorDefecto({ esUnicaPlantillaDelTipo: false })).toBe(true);
  });
});

// ============================================================================
// Responsable: Tejada Rocío
// Funciones: validarCamposPlantilla (3 tests) + calcularEsPorDefecto (2 tests)
// ============================================================================
describe('Tejada Rocío — validarCamposPlantilla y calcularEsPorDefecto', () => {
  test('[validarCamposPlantilla] caso borde: un campo con solo espacios en blanco cuenta como vacío', () => {
    const resultado = validarCamposPlantilla({
      nombre: 'Plantilla X', asunto: 'Asunto', saludo: '   ', cuerpo: 'Cuerpo', firma: 'Firma',
    });
    expect(resultado.valido).toBe(false);
    expect(resultado.camposFaltantes).toEqual(['saludo']);
  });

  test('[validarCamposPlantilla] caso de error: objeto de campos vacío marca los 5 campos como faltantes', () => {
    const resultado = validarCamposPlantilla({});
    expect(resultado.valido).toBe(false);
    expect(resultado.camposFaltantes).toHaveLength(5);
  });

  test('[validarCamposPlantilla] caso normal: no marca como faltante un campo con contenido real', () => {
    const resultado = validarCamposPlantilla({
      nombre: 'X', asunto: 'Y', saludo: 'Z', cuerpo: 'Contenido válido', firma: 'F',
    });
    expect(resultado.camposFaltantes).not.toContain('cuerpo');
  });

  test('[calcularEsPorDefecto] caso borde: al editar sin tick activado, deja de calcularse como por defecto', () => {
    // Nota: el bloqueo real de "no permitir quitar el tick" se valida aparte
    // con puedeQuitarPorDefecto; esta función solo calcula el resultado pedido.
    const resultado = calcularEsPorDefecto({
      existeOtraPlantillaDelTipo: true, tickActivado: false, yaEraPorDefecto: true,
    });
    expect(resultado).toBe(false);
  });

  test('[calcularEsPorDefecto] caso borde: primera plantilla del tipo con tick ya activado también da por defecto', () => {
    const resultado = calcularEsPorDefecto({
      existeOtraPlantillaDelTipo: false, tickActivado: true, yaEraPorDefecto: false,
    });
    expect(resultado).toBe(true);
  });
});

// ============================================================================
// Responsable: Perez Juliana
// Funciones: generarAsunto (3 tests) + validarCamposPlantilla (2 tests)
// ============================================================================
describe('Perez Juliana — generarAsunto y validarCamposPlantilla', () => {
  test('[generarAsunto] caso normal: asunto de notificación al admin por nueva reserva', () => {
    expect(generarAsunto('nueva_reserva_admin', {
      nombreInvitado: 'María Gómez', fecha: '14/05', hora: '10:30',
    })).toBe('Nueva reserva — María Gómez — 14/05 10:30');
  });

  test('[generarAsunto] caso normal: asunto de cancelación al admin', () => {
    expect(generarAsunto('cancelacion_admin', {
      nombreInvitado: 'Juan Pérez', fecha: '12/05', hora: '15:00',
    })).toBe('Cancelación — Juan Pérez — 12/05 15:00');
  });

  test('[generarAsunto] caso de error: tipo de notificación inexistente lanza excepción', () => {
    expect(() => generarAsunto('tipo_inventado', {})).toThrow('Tipo de notificación desconocido');
  });

  test('[validarCamposPlantilla] caso normal: todos los campos completos es válido', () => {
    const resultado = validarCamposPlantilla({
      nombre: 'Confirmación formal', asunto: 'Asunto', saludo: 'Hola', cuerpo: 'Cuerpo', firma: 'Firma',
    });
    expect(resultado).toEqual({ valido: true, camposFaltantes: [] });
  });

  test('[validarCamposPlantilla] caso de error: detecta varios campos faltantes a la vez', () => {
    const resultado = validarCamposPlantilla({ nombre: 'Recordatorio', asunto: '', saludo: undefined, cuerpo: 'Texto', firma: '' });
    expect(resultado.valido).toBe(false);
    expect(resultado.camposFaltantes).toEqual(expect.arrayContaining(['asunto', 'saludo', 'firma']));
  });
});

// ============================================================================
// Responsable: Santibañez Lucia
// Funciones: puedeEliminarPlantilla (3 tests) + construirCuerpoEmail (2 tests)
// ============================================================================
describe('Santibañez Lucia — puedeEliminarPlantilla y construirCuerpoEmail', () => {
  test('[puedeEliminarPlantilla] caso de error: bloquea si es la única plantilla del tipo', () => {
    const resultado = puedeEliminarPlantilla({ cantidadPlantillasDelTipo: 1, esPorDefecto: false });
    expect(resultado).toEqual({ permitido: false, motivo: 'UNICA_DEL_TIPO' });
  });

  test('[puedeEliminarPlantilla] caso de error: bloquea si es la por defecto sin reemplazo designado', () => {
    const resultado = puedeEliminarPlantilla({ cantidadPlantillasDelTipo: 2, esPorDefecto: true });
    expect(resultado).toEqual({ permitido: false, motivo: 'ES_POR_DEFECTO_SIN_REEMPLAZO' });
  });

  test('[puedeEliminarPlantilla] caso normal: permite eliminar una plantilla alternativa cuando hay más de una', () => {
    const resultado = puedeEliminarPlantilla({ cantidadPlantillasDelTipo: 2, esPorDefecto: false });
    expect(resultado).toEqual({ permitido: true, motivo: null });
  });

  test('[construirCuerpoEmail] caso normal: una variable repetida se reemplaza en todas sus apariciones', () => {
    const plantilla = '{nombre_invitado}, confirmamos tu turno {nombre_invitado}.';
    const { cuerpo } = construirCuerpoEmail(plantilla, { nombre_invitado: 'Pedro' });
    expect(cuerpo).toBe('Pedro, confirmamos tu turno Pedro.');
  });

  test('[construirCuerpoEmail] caso borde: variable con valor de string vacío se trata como faltante', () => {
    const plantilla = 'Hola {nombre_invitado}.';
    const { variablesFaltantes } = construirCuerpoEmail(plantilla, { nombre_invitado: '' });
    expect(variablesFaltantes).toEqual(['nombre_invitado']);
  });
});

// ============================================================================
// Responsable: Bataller Paulina
// Funciones: construirCuerpoEmail (3 tests) + enmascararEmail (2 tests)
// ============================================================================
describe('Bataller Paulina — construirCuerpoEmail y enmascararEmail', () => {
  test('[construirCuerpoEmail] caso normal: reemplaza todas las variables presentes', () => {
    const plantilla = 'Hola {nombre_invitado}, tu turno es el {fecha_turno}.';
    const { cuerpo, variablesFaltantes } = construirCuerpoEmail(plantilla, {
      nombre_invitado: 'María García',
      fecha_turno: 'lunes 23 de junio de 2025',
    });
    expect(cuerpo).toBe('Hola María García, tu turno es el lunes 23 de junio de 2025.');
    expect(variablesFaltantes).toEqual([]);
  });

  test('[construirCuerpoEmail] caso de error: detecta variables faltantes y las deja como placeholder', () => {
    const plantilla = 'Hola {nombre_invitado}, tu turno es el {fecha_turno}.';
    const { cuerpo, variablesFaltantes } = construirCuerpoEmail(plantilla, {
      nombre_invitado: 'María García',
    });
    expect(variablesFaltantes).toEqual(['fecha_turno']);
    expect(cuerpo).toContain('{fecha_turno}');
  });

  test('[construirCuerpoEmail] caso borde: plantilla sin variables retorna el mismo texto', () => {
    const plantilla = 'Este es un texto fijo sin variables.';
    const { cuerpo, tieneVariables } = construirCuerpoEmail(plantilla, {});
    expect(cuerpo).toBe(plantilla);
    expect(tieneVariables).toBe(false);
  });

  test('[enmascararEmail] caso normal: conserva los primeros 2 caracteres y enmascara el resto', () => {
    expect(enmascararEmail('usuario@dominio.com')).toBe('us***@dominio.com');
  });

  test('[enmascararEmail] caso borde: local-part de un solo carácter se enmascara igual', () => {
    expect(enmascararEmail('a@x.com')).toBe('a***@x.com');
  });
});


// ============================================================================
// Responsable: Lee Maria Luz
// Funciones: esElegibleParaRecordatorio (3 tests) + puedeEliminarPlantilla (2 tests)
// ============================================================================
describe('Lee Maria Luz — esElegibleParaRecordatorio y puedeEliminarPlantilla', () => {
  test('[esElegibleParaRecordatorio] caso normal: turno a más de 24hs de la reserva es elegible', () => {
    const reserva = new Date('2026-06-10T10:00:00');
    const turno = new Date('2026-06-12T10:00:00'); // +48hs
    expect(esElegibleParaRecordatorio(turno, reserva)).toBe(true);
  });

  test('[esElegibleParaRecordatorio] caso de error: turno a menos de 24hs (reserva de último momento) no es elegible', () => {
    const reserva = new Date('2026-06-10T10:00:00');
    const turno = new Date('2026-06-10T20:00:00'); // +10hs
    expect(esElegibleParaRecordatorio(turno, reserva)).toBe(false);
  });

  test('[esElegibleParaRecordatorio] caso borde: turno a exactamente 24hs es elegible (límite inclusivo)', () => {
    const reserva = new Date('2026-06-10T10:00:00');
    const turno = new Date('2026-06-11T10:00:00'); // +24hs exactas
    expect(esElegibleParaRecordatorio(turno, reserva)).toBe(true);
  });

  test('[puedeEliminarPlantilla] caso borde: sin plantillas registradas del tipo (0) también queda bloqueado', () => {
    const resultado = puedeEliminarPlantilla({ cantidadPlantillasDelTipo: 0, esPorDefecto: false });
    expect(resultado.permitido).toBe(false);
    expect(resultado.motivo).toBe('UNICA_DEL_TIPO');
  });

  test('[puedeEliminarPlantilla] caso normal: con 3 plantillas del tipo y sin ser la por defecto, permite eliminar', () => {
    const resultado = puedeEliminarPlantilla({ cantidadPlantillasDelTipo: 3, esPorDefecto: false });
    expect(resultado.permitido).toBe(true);
  });
});
// ============================================================================
// Responsable: Sanchez Ignacio
// Funciones: enmascararEmail (3 tests) + esElegibleParaRecordatorio (2 tests)
// ============================================================================
describe('Sanchez Ignacio — enmascararEmail y esElegibleParaRecordatorio', () => {
  test('[enmascararEmail] caso normal: funciona igual con dominios con subdominio', () => {
    expect(enmascararEmail('maria.garcia@clinica.agendaya.com')).toBe('ma***@clinica.agendaya.com');
  });

  test('[enmascararEmail] caso de error: email con formato inválido lanza excepción y no se enmascara', () => {
    expect(() => enmascararEmail('usuario@')).toThrow('Email inválido');
  });

  test('[enmascararEmail] caso de error: string vacío lanza excepción', () => {
    expect(() => enmascararEmail('')).toThrow('Email inválido');
  });

  test('[esElegibleParaRecordatorio] caso de error: fecha inválida lanza excepción', () => {
    expect(() => esElegibleParaRecordatorio('fecha-invalida', new Date())).toThrow('Fecha inválida');
  });

  test('[esElegibleParaRecordatorio] caso borde: turno en el pasado respecto de la reserva no es elegible', () => {
    const reserva = new Date('2026-06-10T10:00:00');
    const turno = new Date('2026-06-09T10:00:00'); // turno "anterior" a la reserva
    expect(esElegibleParaRecordatorio(turno, reserva)).toBe(false);
  });
});
