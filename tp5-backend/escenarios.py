"""Datos semilla y preparación del entorno para cada caso de prueba.

Cada CP se ejecuta sobre el entorno reiniciado con sus prerrequisitos.
Desde la pantalla /entorno hay un botón "Preparar" por cada CP.
"""
from datetime import datetime

from app import get_db, reiniciar_db, fijar_reloj, set_cfg, reserva_completa, enviar_cancelacion

ADMIN = dict(nombre="Dr. García", email="admin@agendaya.com", password="Admin1234!",
             telefono="261-555-0001", direccion="Av. San Martín 420, Mendoza")
FIRMA = "Dr. García - Medicina General - Tel 261-555-0001"

PLANTILLAS_BASE = [
    ("Confirmación formal", "Confirmación al invitado",
     "Tu reserva con {nombre_profesional} está confirmada", "Hola {nombre_invitado},",
     "Tu turno quedó confirmado. A continuación te dejamos los detalles."),
    ("Recordatorio estándar", "Recordatorio al invitado",
     "Recordatorio: tu turno con {nombre_profesional} es mañana", "Hola {nombre_invitado},",
     "Te recordamos que mañana tenés turno. Por favor llegá 5 minutos antes."),
    ("Cancelación con motivo", "Cancelación al invitado",
     "Tu turno con {nombre_profesional} fue cancelado", "Hola {nombre_invitado},",
     "Lamentamos informarte que tu turno fue cancelado."),
    ("Aviso nueva reserva", "Nueva reserva al admin",
     "Nueva reserva — {nombre_invitado} — {fecha_corta} {hora_turno} hs", "Hola {nombre_profesional},",
     "Se registró una nueva reserva en tu agenda."),
]


def dt(texto):
    return datetime.fromisoformat(texto)


def preparar_base(reloj="2026-11-16T09:00:00", sin_tipos=()):
    reiniciar_db()
    db = get_db()
    fijar_reloj(dt(reloj))
    set_cfg("servicio_correo", "operativo")
    db.execute("INSERT INTO admin VALUES (1,?,?,?,?,?,'ARG (UTC-3)',1)",
               (ADMIN["nombre"], ADMIN["email"], ADMIN["password"], ADMIN["telefono"], ADMIN["direccion"]))
    db.execute("INSERT INTO tipo_evento VALUES (1,'Consulta inicial - 30 min','Presencial')")
    db.execute("INSERT INTO tipo_evento VALUES (2,'Seguimiento - 15 min','Presencial')")
    for nombre, tipo, asunto, saludo, cuerpo in PLANTILLAS_BASE:
        if tipo in sin_tipos:
            continue
        agregar_plantilla(nombre, tipo, asunto, saludo, cuerpo, 1)
    db.commit()


def agregar_plantilla(nombre, tipo, asunto, saludo, cuerpo, por_defecto):
    get_db().execute(
        "INSERT INTO plantilla (nombre, tipo, asunto, saludo, cuerpo, firma, por_defecto, autor, creada_en) "
        "VALUES (?,?,?,?,?,?,?,?,?)",
        (nombre, tipo, asunto, saludo, cuerpo, FIRMA, por_defecto, ADMIN["email"], "2026-11-01T10:00:00"))


def agregar_reserva(rid, evento_id, fecha_hora, nombre, email, telefono, creada_en, nota=""):
    get_db().execute(
        "INSERT INTO reserva (id, tipo_evento_id, fecha_hora, invitado_nombre, invitado_email, "
        "invitado_telefono, nota, estado, creada_en, recordatorio_estado) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (rid, evento_id, fecha_hora, nombre, email, telefono, nota, "Confirmada", creada_en, "programado"))


def agregar_notificacion(tipo, destinatario, asunto, plantilla, enviada_en, estado="enviado"):
    get_db().execute(
        "INSERT INTO notificacion (tipo, destinatario, asunto, cuerpo_html, plantilla_nombre, reserva_id, "
        "estado, intentos, enviada_en) VALUES (?,?,?,?,?,NULL,?,1,?)",
        (tipo, destinatario, asunto, "<p>(email de datos semilla)</p>", plantilla, estado, enviada_en))


# --- escenarios por caso de prueba -----------------------------------------
def cp_base():
    preparar_base()


def cp_reserva_1042():
    preparar_base()
    agregar_reserva(1042, 1, "2026-11-18T10:30:00", "María Gómez", "maria@email.com", "261-555-9999",
                    "2026-11-16T08:00:00")


def cp005():
    preparar_base()
    agregar_reserva(1, 1, "2026-11-18T10:30:00", "Marta", "marta@email.com", "261-555-4321",
                    "2026-11-16T08:30:00")


def cp006():
    preparar_base(reloj="2026-11-17T14:00:00")


def cp007():
    preparar_base(sin_tipos=("Recordatorio al invitado",))


def cp009():
    preparar_base()
    db = get_db()
    pid = db.execute("SELECT id FROM plantilla WHERE nombre='Confirmación formal'").fetchone()[0]
    db.execute("INSERT INTO plantilla_version (plantilla_id, asunto, saludo, cuerpo, firma, guardada_en, autor) "
               "VALUES (?,?,?,?,?,?,?)", (pid, "Tu turno con {nombre_profesional} está confirmado",
                                          "Hola {nombre_invitado},", "Gracias por reservar tu turno.",
                                          FIRMA, "2026-10-20T10:00:00", ADMIN["email"]))


def cp011():
    preparar_base()
    agregar_plantilla("Confirmación breve", "Confirmación al invitado",
                      "Turno confirmado", "Hola {nombre_invitado},", "Te esperamos.", 0)
    agregar_notificacion("Confirmación", "lucas@email.com", "Turno confirmado", "Confirmación breve",
                         "2026-11-10T11:00:00")
    agregar_notificacion("Confirmación", "sofia@email.com", "Turno confirmado", "Confirmación breve",
                         "2026-11-12T16:30:00")


def cp014():
    preparar_base()
    agregar_reserva(1051, 2, "2026-11-19T11:30:00", "Carlos Ruiz", "carlos.ruiz@email.com", "261-555-7777",
                    "2026-11-15T09:00:00")


def cp015():
    cp_reserva_1042()
    db = get_db()
    db.execute("UPDATE reserva SET estado='Cancelada', cancelada_por='admin', recordatorio_estado='cancelado', "
               "motivo_cancelacion='Surgió un imprevisto. Disculpá las molestias.' WHERE id=1042")
    enviar_cancelacion(reserva_completa(1042))


def cp016():
    preparar_base(reloj="2026-11-19T09:00:00")
    agregar_notificacion("Confirmación", "maria@email.com", "Tu reserva con Dr. García está confirmada",
                         "Confirmación formal", "2026-11-16T09:00:00")
    agregar_notificacion("Recordatorio", "pedro@email.com", "Recordatorio: tu turno con Dr. García es mañana",
                         "Recordatorio estándar", "2026-11-17T10:30:00")
    agregar_notificacion("Cancelación", "carlos.ruiz@email.com", "Tu turno con Dr. García fue cancelado",
                         "Cancelación con motivo", "2026-11-18T12:00:00")


ESCENARIOS = {
    "CP-001": ("Base: plantillas por defecto, turno 18/11/2026 10:30 libre", cp_base),
    "CP-002": ("Base: plantillas por defecto, turno 18/11/2026 10:30 libre", cp_base),
    "CP-003": ("Base: badge del admin en 0", cp_base),
    "CP-004": ("Reserva #1042 de María Gómez confirmada, badge en 0", cp_reserva_1042),
    "CP-005": ("Reserva de Marta 18/11/2026 10:30 con recordatorio programado", cp005),
    "CP-006": ("Reloj en martes 17/11/2026 14:00, turno de las 20:00 libre", cp006),
    "CP-007": ("Sin plantillas del tipo 'Recordatorio al invitado'", cp007),
    "CP-008": ("Existe 'Confirmación formal'", cp_base),
    "CP-009": ("'Confirmación formal' por defecto con una versión en el historial", cp009),
    "CP-010": ("'Cancelación con motivo' es la única de su tipo", cp_base),
    "CP-011": ("'Confirmación formal' ★ + 'Confirmación breve' con envíos previos", cp011),
    "CP-012": ("'Recordatorio estándar' es la única de su tipo", cp_base),
    "CP-013": ("Reserva #1042 de María Gómez confirmada", cp_reserva_1042),
    "CP-014": ("Reserva #1051 de Carlos Ruiz confirmada", cp014),
    "CP-015": ("María Gómez recibió el email de cancelación de la reserva #1042", cp015),
    "CP-016": ("Historial con 3 notificaciones enviadas y ninguna fallida", cp016),
}
