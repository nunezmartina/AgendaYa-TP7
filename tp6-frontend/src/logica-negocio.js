/**
 * AgendaYA — Módulo M06: Notificaciones y Comunicaciones
 * Lógica de negocio mínima para poder testear unitariamente (Tarea C del TP6).
 * Basada en los requerimientos M06-R01F a M06-R05F (TP1) y las historias
 * US-M06-001 a US-M06-009 (TP2).
 */

// ---------------------------------------------------------------------------
// 1. Validación de formato de email (soporta M06-R01F: no se envía nada si el
//    email del invitado tiene formato inválido)
// ---------------------------------------------------------------------------
function esEmailValido(email) {
  if (typeof email !== 'string' || email.trim() === '') return false;
  // Formato simple: algo@algo.algo, sin espacios
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email.trim());
}

// ---------------------------------------------------------------------------
// 2. Generación del asunto del email según el tipo de notificación
//    (M06-R01F, R02F, R03F, R05F: cada tipo tiene un patrón de asunto fijo)
// ---------------------------------------------------------------------------
const TIPOS_NOTIFICACION = [
  'confirmacion',
  'recordatorio',
  'cancelacion',
  'nueva_reserva_admin',
  'cancelacion_admin',
];

function generarAsunto(tipo, datos = {}) {
  const { nombreProfesional, nombreInvitado, fecha, hora } = datos;

  if (!TIPOS_NOTIFICACION.includes(tipo)) {
    throw new Error(`Tipo de notificación desconocido: ${tipo}`);
  }

  switch (tipo) {
    case 'confirmacion':
      if (!nombreProfesional) throw new Error('Falta nombreProfesional para el asunto de confirmación');
      return `Tu reserva con ${nombreProfesional} está confirmada`;
    case 'recordatorio':
      if (!nombreProfesional) throw new Error('Falta nombreProfesional para el asunto de recordatorio');
      return `Recordatorio: tu turno con ${nombreProfesional} es mañana`;
    case 'cancelacion':
      if (!nombreProfesional) throw new Error('Falta nombreProfesional para el asunto de cancelación');
      return `Tu reserva con ${nombreProfesional} fue cancelada`;
    case 'nueva_reserva_admin':
      if (!nombreInvitado || !fecha || !hora) throw new Error('Faltan datos para el asunto de nueva reserva');
      return `Nueva reserva — ${nombreInvitado} — ${fecha} ${hora}`;
    case 'cancelacion_admin':
      if (!nombreInvitado || !fecha || !hora) throw new Error('Faltan datos para el asunto de cancelación (admin)');
      return `Cancelación — ${nombreInvitado} — ${fecha} ${hora}`;
    default:
      throw new Error('Tipo no soportado');
  }
}

// ---------------------------------------------------------------------------
// 3. Lógica del tick "Por defecto" al crear/editar una plantilla
//    (M06-R04F — ALTA/MODIFICACIÓN, US-M06-004 y US-M06-005)
//
//    Devuelve si la plantilla que se está guardando queda (o sigue) siendo
//    la plantilla por defecto de su tipo.
// ---------------------------------------------------------------------------
function calcularEsPorDefecto({ existeOtraPlantillaDelTipo, tickActivado, yaEraPorDefecto = false }) {
  // Si no existe ninguna otra plantilla de ese tipo, la nueva siempre
  // queda como por defecto, sin importar el tick.
  if (!existeOtraPlantillaDelTipo) return true;

  // Si ya era la por defecto (edición) y el tick sigue activado, se conserva.
  if (yaEraPorDefecto && tickActivado) return true;

  // Si ya era la por defecto pero el admin intenta desactivar el tick,
  // esto solo se permite si existe otra plantilla del tipo (regla validada
  // aparte por puedeQuitarPorDefecto). Esta función solo calcula el resultado
  // "ideal" pedido por el usuario.
  return !!tickActivado;
}

function puedeQuitarPorDefecto({ esUnicaPlantillaDelTipo }) {
  // No se puede desactivar el tick "por defecto" si es la única plantilla del tipo.
  return !esUnicaPlantillaDelTipo;
}

// ---------------------------------------------------------------------------
// 4. Construcción del cuerpo de un email a partir de una plantilla con
//    variables dinámicas ({nombre_invitado}, {fecha_turno}, etc.)
//    (M06-R04F — Vista previa, US-M06-005 Escenario 2)
// ---------------------------------------------------------------------------
function construirCuerpoEmail(plantilla, variables = {}) {
  if (typeof plantilla !== 'string') {
    throw new Error('La plantilla debe ser un string');
  }

  const variablesEncontradas = plantilla.match(/\{[a-zA-Z_]+\}/g) || [];
  const variablesFaltantes = [];

  const cuerpo = plantilla.replace(/\{([a-zA-Z_]+)\}/g, (match, nombreVar) => {
    if (Object.prototype.hasOwnProperty.call(variables, nombreVar) && variables[nombreVar] !== undefined && variables[nombreVar] !== '') {
      return String(variables[nombreVar]);
    }
    variablesFaltantes.push(nombreVar);
    return match; // se deja el placeholder tal cual si falta el dato
  });

  return {
    cuerpo,
    variablesFaltantes: [...new Set(variablesFaltantes)],
    tieneVariables: variablesEncontradas.length > 0,
  };
}

// ---------------------------------------------------------------------------
// 5. Validación de si se puede eliminar una plantilla (BAJA)
//    (M06-R04F — BAJA, US-M06-006)
// ---------------------------------------------------------------------------
function puedeEliminarPlantilla({ cantidadPlantillasDelTipo, esPorDefecto }) {
  if (cantidadPlantillasDelTipo <= 1) {
    return { permitido: false, motivo: 'UNICA_DEL_TIPO' };
  }
  if (esPorDefecto) {
    return { permitido: false, motivo: 'ES_POR_DEFECTO_SIN_REEMPLAZO' };
  }
  return { permitido: true, motivo: null };
}

// ---------------------------------------------------------------------------
// 6. Elegibilidad de una reserva para recibir el recordatorio 24hs antes
//    (M06-R03F, US-M06-003 — no se programa si falta menos de 24hs)
// ---------------------------------------------------------------------------
function esElegibleParaRecordatorio(fechaHoraTurno, fechaHoraReserva = new Date()) {
  const turno = fechaHoraTurno instanceof Date ? fechaHoraTurno : new Date(fechaHoraTurno);
  const reserva = fechaHoraReserva instanceof Date ? fechaHoraReserva : new Date(fechaHoraReserva);

  if (isNaN(turno.getTime()) || isNaN(reserva.getTime())) {
    throw new Error('Fecha inválida');
  }

  const VEINTICUATRO_HS_MS = 24 * 60 * 60 * 1000;
  const diferencia = turno.getTime() - reserva.getTime();

  // Si el turno ya pasó, o falta menos de 24hs desde el momento de la
  // reserva, no corresponde programar recordatorio.
  return diferencia >= VEINTICUATRO_HS_MS;
}

// ---------------------------------------------------------------------------
// 7. Validación de campos obligatorios del formulario de plantilla
//    (M06-R04F — ALTA, criterio de aceptación 5.4 del TP6: "campo vacío")
// ---------------------------------------------------------------------------
function validarCamposPlantilla(campos = {}) {
  const obligatorios = ['nombre', 'asunto', 'saludo', 'cuerpo', 'firma'];
  const camposFaltantes = obligatorios.filter((campo) => {
    const valor = campos[campo];
    return valor === undefined || valor === null || String(valor).trim() === '';
  });
  return { valido: camposFaltantes.length === 0, camposFaltantes };
}

// ---------------------------------------------------------------------------
// 8. Enmascarado del email del destinatario para el historial de
//    notificaciones (US-M06-009: "destinatario enmascarado: us***@email.com")
// ---------------------------------------------------------------------------
function enmascararEmail(email) {
  if (!esEmailValido(email)) {
    throw new Error('Email inválido, no se puede enmascarar');
  }
  const [local, dominio] = email.trim().split('@');
  const visibles = local.slice(0, 2);
  return `${visibles}***@${dominio}`;
}

module.exports = {
  esEmailValido,
  generarAsunto,
  calcularEsPorDefecto,
  puedeQuitarPorDefecto,
  construirCuerpoEmail,
  puedeEliminarPlantilla,
  esElegibleParaRecordatorio,
  validarCamposPlantilla,
  enmascararEmail,
};
