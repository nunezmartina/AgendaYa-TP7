"""AgendaYA - Módulo M06 Notificaciones y Comunicaciones.

Implementación mínima para ejecutar los casos de prueba del TP N°5
(Ingeniería y Calidad de Software - Grupo 9).

Los emails no se envían a un servidor real: se guardan en la tabla
`notificacion`, que funciona como buzón de pruebas (/buzon) y como
historial de envíos (/admin/historial), igual que Mailtrap.
El reloj del sistema se puede simular desde /entorno para probar
los recordatorios de 24 horas.
"""

import os
import re
import sqlite3
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, g, redirect, render_template, request, session, url_for, flash, jsonify, abort

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("AGENDAYA_DB", os.path.join(BASE_DIR, "agendaya.db"))

app = Flask(__name__)
app.secret_key = "agendaya-tp5-grupo9"

# ---------------------------------------------------------------------------
# Constantes del dominio (TP1 / TP2)
# ---------------------------------------------------------------------------
TIPOS_PLANTILLA = [
    "Confirmación al invitado",
    "Recordatorio al invitado",
    "Cancelación al invitado",
    "Nueva reserva al admin",
]
LIMITES = {"nombre": 80, "asunto": 100, "saludo": 200, "cuerpo": 1000, "firma": 300}
TEXTOS_POR_DEFECTO = {
    "asunto": "Notificación de AgendaYA",
    "saludo": "Hola {nombre_invitado},",
    "cuerpo": "Te escribimos por tu turno en AgendaYA.",
    "firma": "{nombre_profesional}",
}
MAX_VERSIONES = 5
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
MSG_EMAIL_INVALIDO = "El email ingresado no es válido. Ej: usuario@dominio.com"
MSG_NOMBRE_DUPLICADO = "Ya existe una plantilla con ese nombre. Por favor usá un nombre diferente"
MSG_TICK_UNICA = (
    "No podés quitar el estado por defecto si es la única plantilla de este tipo. "
    "Creá otra y marcala como por defecto primero."
)
MSG_ELIMINAR_UNICA = "No podés eliminar la única plantilla de este tipo. Creá otra antes de eliminar esta."
MSG_ELIMINAR_DEFECTO = (
    "Esta plantilla es la por defecto. Primero designar otra como por defecto "
    "desde Editar, y luego podrás eliminar esta."
)

DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = [
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
]


# ---------------------------------------------------------------------------
# Base de datos
# ---------------------------------------------------------------------------
SCHEMA = """
CREATE TABLE config (clave TEXT PRIMARY KEY, valor TEXT);
CREATE TABLE admin (
    id INTEGER PRIMARY KEY, nombre TEXT, email TEXT, password TEXT, telefono TEXT,
    direccion TEXT, zona_horaria TEXT, recordatorios_activos INTEGER);
CREATE TABLE tipo_evento (id INTEGER PRIMARY KEY, nombre TEXT, modalidad TEXT);
CREATE TABLE reserva (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tipo_evento_id INTEGER, fecha_hora TEXT,
    invitado_nombre TEXT, invitado_email TEXT, invitado_telefono TEXT, nota TEXT,
    estado TEXT, creada_en TEXT, recordatorio_estado TEXT, recordatorio_enviado_en TEXT,
    motivo_cancelacion TEXT, cancelada_por TEXT, aviso_panel TEXT);
CREATE TABLE plantilla (
    id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT UNIQUE, tipo TEXT, asunto TEXT,
    saludo TEXT, cuerpo TEXT, firma TEXT, por_defecto INTEGER, autor TEXT,
    creada_en TEXT, modificada_por TEXT, modificada_en TEXT);
CREATE TABLE plantilla_version (
    id INTEGER PRIMARY KEY AUTOINCREMENT, plantilla_id INTEGER, asunto TEXT, saludo TEXT,
    cuerpo TEXT, firma TEXT, guardada_en TEXT, autor TEXT);
CREATE TABLE notificacion (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT, destinatario TEXT, asunto TEXT,
    cuerpo_html TEXT, plantilla_nombre TEXT, reserva_id INTEGER, estado TEXT,
    intentos INTEGER, enviada_en TEXT);
CREATE TABLE alerta (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT, texto TEXT, creada_en TEXT, leida INTEGER);
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.commit()
        db.close()


TABLAS = ["config", "admin", "tipo_evento", "reserva", "plantilla", "plantilla_version", "notificacion", "alerta"]


def reiniciar_db():
    """Borra y recrea todas las tablas sobre la conexión actual."""
    db = get_db()
    db.executescript("".join(f"DROP TABLE IF EXISTS {t};" for t in TABLAS) + SCHEMA)


# ---------------------------------------------------------------------------
# Reloj simulado del entorno de test
# ---------------------------------------------------------------------------
def cfg(clave, default=None):
    row = get_db().execute("SELECT valor FROM config WHERE clave=?", (clave,)).fetchone()
    return row["valor"] if row else default


def set_cfg(clave, valor):
    get_db().execute("INSERT OR REPLACE INTO config (clave, valor) VALUES (?, ?)", (clave, valor))


def ahora():
    base = cfg("reloj_base")
    if not base:
        return datetime.now().replace(microsecond=0)
    fijado_en = datetime.fromisoformat(cfg("reloj_fijado_en"))
    return (datetime.fromisoformat(base) + (datetime.now() - fijado_en)).replace(microsecond=0)


def fijar_reloj(momento):
    set_cfg("reloj_base", momento.isoformat())
    set_cfg("reloj_fijado_en", datetime.now().isoformat())


# ---------------------------------------------------------------------------
# Utilidades de formato
# ---------------------------------------------------------------------------
def fecha_larga(dt):
    return f"{DIAS[dt.weekday()]} {dt.day} de {MESES[dt.month - 1]} de {dt.year}"


def fecha_corta(dt):
    return dt.strftime("%d/%m/%Y")


def enmascarar(email):
    usuario, _, dominio = email.partition("@")
    return f"{usuario[:2]}***@{dominio}"


app.jinja_env.filters["fecha_larga"] = lambda s: fecha_larga(datetime.fromisoformat(s))
app.jinja_env.filters["fecha_corta"] = lambda s: fecha_corta(datetime.fromisoformat(s))
app.jinja_env.filters["hora"] = lambda s: datetime.fromisoformat(s).strftime("%H:%M")
app.jinja_env.filters["fh"] = lambda s: datetime.fromisoformat(s).strftime("%d/%m/%Y %H:%M:%S") if s else ""
app.jinja_env.filters["enmascarar"] = enmascarar


def admin_actual():
    return get_db().execute("SELECT * FROM admin WHERE id=1").fetchone()


def reserva_completa(rid):
    return (
        get_db()
        .execute(
            "SELECT r.*, t.nombre AS evento, t.modalidad FROM reserva r "
            "JOIN tipo_evento t ON t.id=r.tipo_evento_id WHERE r.id=?",
            (rid,),
        )
        .fetchone()
    )


# ---------------------------------------------------------------------------
# Envío de emails (M06-R01F, R02F, R03F, R05F)
# ---------------------------------------------------------------------------
def plantilla_por_defecto(tipo):
    return get_db().execute("SELECT * FROM plantilla WHERE tipo=? AND por_defecto=1", (tipo,)).fetchone()


def variables(reserva, admin):
    dt = datetime.fromisoformat(reserva["fecha_hora"])
    return {
        "nombre_invitado": reserva["invitado_nombre"],
        "nombre_profesional": admin["nombre"],
        "fecha_turno": fecha_larga(dt),
        "fecha_corta": fecha_corta(dt),
        "hora_turno": dt.strftime("%H:%M"),
        "tipo_evento": reserva["evento"],
    }


def completar(texto, vars_):
    for k, v in vars_.items():
        texto = texto.replace("{" + k + "}", v)
    return texto


def registrar_envio(tipo, destinatario, asunto, cuerpo_html, plantilla_nombre, reserva_id):
    """Simula el envío. Si el servicio de correo está caído se reintenta 3 veces
    (US-M06-001, Escenario 3) y queda registrado como 'fallido'."""
    servicio_ok = cfg("servicio_correo", "operativo") == "operativo"
    estado = "enviado" if servicio_ok else "fallido"
    intentos = 1 if servicio_ok else 3
    get_db().execute(
        "INSERT INTO notificacion (tipo, destinatario, asunto, cuerpo_html, plantilla_nombre, "
        "reserva_id, estado, intentos, enviada_en) VALUES (?,?,?,?,?,?,?,?,?)",
        (tipo, destinatario, asunto, cuerpo_html, plantilla_nombre, reserva_id, estado, intentos, ahora().isoformat()),
    )
    return estado


def detalle_turno_html(reserva, admin, tachado=False):
    dt = datetime.fromisoformat(reserva["fecha_hora"])
    evento = f"<s>{reserva['evento']}</s>" if tachado else reserva["evento"]
    filas = [
        ("Tipo de evento", evento),
        ("Fecha", fecha_larga(dt)),
        ("Hora", dt.strftime("%H:%M") + " hs (ARG)"),
        ("Profesional", admin["nombre"]),
        ("Modalidad", reserva["modalidad"]),
    ]
    if reserva["modalidad"] == "Presencial":
        filas.append(("Dirección", admin["direccion"]))
    filas.append(("Contacto del profesional", admin["telefono"]))
    return "<table class='mail-det'>" + "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in filas) + "</table>"


def email_desde_plantilla(tipo_plantilla, tipo_notif, reserva, extra_html=""):
    admin = admin_actual()
    plantilla = plantilla_por_defecto(tipo_plantilla)
    if plantilla is None:
        return None
    v = variables(reserva, admin)
    asunto = completar(plantilla["asunto"], v)
    cuerpo = (
        f"<p>{completar(plantilla['saludo'], v)}</p><p>{completar(plantilla['cuerpo'], v)}</p>"
        f"{detalle_turno_html(reserva, admin, tachado=(tipo_notif == 'Cancelación'))}"
        f"{extra_html}<p class='firma'>{completar(plantilla['firma'], v)}</p>"
    )
    return registrar_envio(tipo_notif, reserva["invitado_email"], asunto, cuerpo, plantilla["nombre"], reserva["id"])


def enviar_confirmacion(reserva):
    boton = f"<p><a class='btn' href='/reserva/{reserva['id']}'>Ver detalles de mi reserva</a></p>"
    return email_desde_plantilla("Confirmación al invitado", "Confirmación", reserva, boton)


def enviar_recordatorio(reserva):
    return email_desde_plantilla("Recordatorio al invitado", "Recordatorio", reserva)


def enviar_cancelacion(reserva):
    admin = admin_actual()
    if reserva["motivo_cancelacion"]:
        motivo = f"<p><strong>Motivo:</strong> {reserva['motivo_cancelacion']}</p>"
    else:
        motivo = f"<p>Para más información, comunicate con {admin['nombre']} al {admin['telefono']}.</p>"
    boton = "<p><a class='btn' href='/agenda/dr-garcia'>Reservar nuevo turno</a></p>"
    return email_desde_plantilla("Cancelación al invitado", "Cancelación", reserva, motivo + boton)


def notificar_admin(tipo, reserva):
    """M06-R02F: email + alerta en el panel. Solo ante acciones del invitado."""
    admin = admin_actual()
    dt = datetime.fromisoformat(reserva["fecha_hora"])
    cuando = f"{fecha_corta(dt)} {dt.strftime('%H:%M')} hs"
    if tipo == "nueva":
        plantilla = plantilla_por_defecto("Nueva reserva al admin")
        asunto = f"Nueva reserva — {reserva['invitado_nombre']} — {cuando}"
        nombre_plantilla = plantilla["nombre"] if plantilla else None
        filas = [
            ("Invitado", reserva["invitado_nombre"]),
            ("Email", reserva["invitado_email"]),
            ("Teléfono", reserva["invitado_telefono"] or "—"),
            ("Tipo de evento", reserva["evento"]),
            ("Fecha", fecha_corta(dt)),
            ("Hora", dt.strftime("%H:%M") + " hs"),
            ("Nota del invitado", reserva["nota"] or "—"),
        ]
        texto_alerta = f"Nueva reserva de {reserva['invitado_nombre']} — {cuando}"
        tipo_alerta = "Nueva reserva"
    else:
        asunto = f"Cancelación — {reserva['invitado_nombre']} — {cuando}"
        nombre_plantilla = None
        filas = [
            ("Invitado", reserva["invitado_nombre"]),
            ("Turno cancelado", f"{reserva['evento']} — {cuando}"),
            ("Motivo", reserva["motivo_cancelacion"] or "—"),
            ("Horario", "Liberado"),
        ]
        texto_alerta = f"Cancelación de {reserva['invitado_nombre']} — {cuando}"
        tipo_alerta = "Cancelación"
    cuerpo = "<table class='mail-det'>" + "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in filas) + "</table>"
    registrar_envio("Aviso al admin", admin["email"], asunto, cuerpo, nombre_plantilla, reserva["id"])
    get_db().execute(
        "INSERT INTO alerta (tipo, texto, creada_en, leida) VALUES (?,?,?,0)",
        (tipo_alerta, texto_alerta, ahora().isoformat()),
    )


# ---------------------------------------------------------------------------
# Scheduler de recordatorios (M06-R03F)
# ---------------------------------------------------------------------------
def ejecutar_job_recordatorios():
    db = get_db()
    momento = ahora()
    pendientes = db.execute(
        "SELECT id FROM reserva WHERE estado='Confirmada' AND recordatorio_estado='programado'"
    ).fetchall()
    enviados = 0
    for row in pendientes:
        r = reserva_completa(row["id"])
        turno = datetime.fromisoformat(r["fecha_hora"])
        falta = turno - momento
        # Tolerancia de ±5 minutos (criterio SMART de US-M06-003)
        if timedelta(0) < falta <= timedelta(hours=24, minutes=5):
            estado = enviar_recordatorio(r)
            db.execute(
                "UPDATE reserva SET recordatorio_estado=?, recordatorio_enviado_en=? WHERE id=?",
                ("enviado" if estado == "enviado" else "fallido", momento.isoformat(), r["id"]),
            )
            enviados += 1
    return enviados


@app.before_request
def scheduler():
    """Simula el scheduler: se ejecuta en cada request (el reloj puede estar simulado)."""
    if os.path.exists(DB_PATH) and request.endpoint not in ("static",):
        try:
            ejecutar_job_recordatorios()
        except sqlite3.OperationalError:
            pass


# ---------------------------------------------------------------------------
# Autenticación del administrador (M01, simplificado)
# ---------------------------------------------------------------------------
def login_requerido(f):
    @wraps(f)
    def envoltura(*a, **kw):
        if not session.get("admin"):
            return redirect(url_for("login", siguiente=request.path))
        return f(*a, **kw)

    return envoltura


@app.context_processor
def contexto():
    datos = {"reloj": None, "badge": 0, "logueado": bool(session.get("admin"))}
    try:
        datos["reloj"] = ahora()
        datos["badge"] = get_db().execute("SELECT COUNT(*) FROM alerta WHERE leida=0").fetchone()[0]
        datos["correo_ok"] = cfg("servicio_correo", "operativo") == "operativo"
    except sqlite3.OperationalError:
        pass
    datos["fecha_larga"] = fecha_larga
    return datos


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        a = admin_actual()
        if request.form.get("email") == a["email"] and request.form.get("password") == a["password"]:
            session["admin"] = a["email"]
            return redirect(request.args.get("siguiente") or url_for("panel"))
        error = "Credenciales inválidas"
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("agenda"))


# ---------------------------------------------------------------------------
# Booking público (M04, lo necesario para disparar M06)
# ---------------------------------------------------------------------------
HORARIOS = [f"{h:02d}:{m:02d}" for h in range(9, 21) for m in (0, 30) if not (h == 20 and m == 30)]
DIAS_AGENDA = [datetime(2026, 11, d) for d in range(16, 21)]


def turnos_disponibles(evento_id):
    db = get_db()
    ocupados = {r["fecha_hora"] for r in db.execute("SELECT fecha_hora FROM reserva WHERE estado='Confirmada'")}
    momento = ahora()
    agenda = []
    for dia in DIAS_AGENDA:
        libres = []
        for h in HORARIOS:
            dt = datetime.fromisoformat(f"{dia.date().isoformat()}T{h}:00")
            if dt > momento and dt.isoformat() not in ocupados:
                libres.append(dt)
        agenda.append((dia, libres))
    return agenda


@app.route("/")
def inicio():
    return redirect(url_for("agenda"))


@app.route("/agenda/dr-garcia")
def agenda():
    eventos = get_db().execute("SELECT * FROM tipo_evento").fetchall()
    return render_template("agenda.html", eventos=eventos, admin=admin_actual())


@app.route("/agenda/dr-garcia/<int:evento_id>")
def agenda_evento(evento_id):
    evento = get_db().execute("SELECT * FROM tipo_evento WHERE id=?", (evento_id,)).fetchone() or abort(404)
    return render_template("turnos.html", evento=evento, agenda=turnos_disponibles(evento_id), admin=admin_actual())


@app.route("/agenda/dr-garcia/<int:evento_id>/reservar", methods=["GET", "POST"])
def reservar(evento_id):
    db = get_db()
    evento = db.execute("SELECT * FROM tipo_evento WHERE id=?", (evento_id,)).fetchone() or abort(404)
    fh = request.values.get("fh")
    datos = {k: request.form.get(k, "").strip() for k in ("nombre", "email", "telefono", "nota")}
    errores = {}
    if request.method == "POST":
        if not datos["nombre"]:
            errores["nombre"] = "Ingresá tu nombre."
        if not EMAIL_RE.match(datos["email"]):
            errores["email"] = MSG_EMAIL_INVALIDO  # US-M06-001, Escenario 2
        ocupado = db.execute("SELECT 1 FROM reserva WHERE fecha_hora=? AND estado='Confirmada'", (fh,)).fetchone()
        if ocupado:
            errores["turno"] = "Ese turno ya no está disponible."
        if not errores:
            momento = ahora()
            turno = datetime.fromisoformat(fh)
            admin = admin_actual()
            # US-M06-003 Escenario 3: menos de 24 hs de anticipación -> no aplica
            if turno - momento > timedelta(hours=24) and admin["recordatorios_activos"]:
                recordatorio = "programado"
            else:
                recordatorio = "no aplica"
            cur = db.execute(
                "INSERT INTO reserva (tipo_evento_id, fecha_hora, invitado_nombre, invitado_email, "
                "invitado_telefono, nota, estado, creada_en, recordatorio_estado) "
                "VALUES (?,?,?,?,?,?,?,?,?)",
                (
                    evento_id,
                    fh,
                    datos["nombre"],
                    datos["email"],
                    datos["telefono"],
                    datos["nota"],
                    "Confirmada",
                    momento.isoformat(),
                    recordatorio,
                ),
            )
            r = reserva_completa(cur.lastrowid)
            enviar_confirmacion(r)  # M06-R01F
            notificar_admin("nueva", r)  # M06-R02F
            return redirect(url_for("reserva_confirmada", rid=r["id"]))
    return render_template("reservar.html", evento=evento, fh=fh, datos=datos, errores=errores, admin=admin_actual())


@app.route("/confirmada/<int:rid>")
def reserva_confirmada(rid):
    return render_template("confirmada.html", r=reserva_completa(rid))


@app.route("/reserva/<int:rid>", methods=["GET", "POST"])
def reserva_invitado(rid):
    r = reserva_completa(rid) or abort(404)
    if request.method == "POST" and r["estado"] == "Confirmada":
        get_db().execute(
            "UPDATE reserva SET estado='Cancelada', cancelada_por='invitado', motivo_cancelacion=?, "
            "recordatorio_estado=CASE WHEN recordatorio_estado='programado' THEN 'cancelado' "
            "ELSE recordatorio_estado END WHERE id=?",
            (request.form.get("motivo", "").strip(), rid),
        )
        notificar_admin("cancelacion", reserva_completa(rid))  # US-M06-002, Escenario 2
        flash("Tu reserva fue cancelada.")
        return redirect(url_for("reserva_invitado", rid=rid))
    return render_template("reserva_invitado.html", r=r, admin=admin_actual())


# ---------------------------------------------------------------------------
# Panel del administrador
# ---------------------------------------------------------------------------
@app.route("/admin")
@login_requerido
def panel():
    db = get_db()
    reservas = db.execute(
        "SELECT r.*, t.nombre AS evento FROM reserva r JOIN tipo_evento t ON t.id=r.tipo_evento_id "
        "ORDER BY r.fecha_hora"
    ).fetchall()
    alertas = db.execute("SELECT * FROM alerta ORDER BY id DESC LIMIT 10").fetchall()
    return render_template("panel.html", reservas=reservas, alertas=alertas)


@app.route("/admin/api/alertas")
@login_requerido
def api_alertas():
    db = get_db()
    alertas = db.execute("SELECT * FROM alerta ORDER BY id DESC LIMIT 10").fetchall()
    return jsonify(
        badge=db.execute("SELECT COUNT(*) FROM alerta WHERE leida=0").fetchone()[0],
        html=render_template("_alertas.html", alertas=alertas),
    )


@app.route("/admin/alertas/leidas", methods=["POST"])
@login_requerido
def marcar_leidas():
    get_db().execute("UPDATE alerta SET leida=1")
    return redirect(url_for("panel"))


@app.route("/admin/reservas/<int:rid>")
@login_requerido
def detalle_reserva(rid):
    return render_template("reserva_admin.html", r=reserva_completa(rid) or abort(404))


@app.route("/admin/reservas/<int:rid>/cancelar", methods=["GET", "POST"])
@login_requerido
def cancelar_reserva(rid):
    """M05 + M06-R05F. El admin no recibe aviso de su propia acción (M06-R02F)."""
    db = get_db()
    r = reserva_completa(rid) or abort(404)
    if request.method == "POST" and r["estado"] == "Confirmada":
        motivo = request.form.get("motivo", "").strip()
        notificar = request.form.get("notificar") == "on"
        db.execute(
            "UPDATE reserva SET estado='Cancelada', cancelada_por='admin', motivo_cancelacion=?, "
            "recordatorio_estado=CASE WHEN recordatorio_estado='programado' THEN 'cancelado' "
            "ELSE recordatorio_estado END WHERE id=?",
            (motivo, rid),
        )
        r = reserva_completa(rid)
        if notificar:
            enviar_cancelacion(r)
            aviso = f"Email de cancelación enviado a {r['invitado_email']} — {ahora().strftime('%d/%m/%Y %H:%M:%S')}"
        else:
            aviso = "Reserva cancelada. Notificación al invitado: desactivada"
        db.execute("UPDATE reserva SET aviso_panel=? WHERE id=?", (aviso, rid))
        return redirect(url_for("detalle_reserva", rid=rid))
    return render_template("cancelar.html", r=r)


@app.route("/admin/recordatorios", methods=["GET", "POST"])
@login_requerido
def recordatorios():
    if request.method == "POST":
        n = ejecutar_job_recordatorios()
        flash(f"Job de recordatorios ejecutado: {n} recordatorio(s) enviado(s).")
        return redirect(url_for("recordatorios"))
    filas = (
        get_db()
        .execute(
            "SELECT r.*, t.nombre AS evento FROM reserva r JOIN tipo_evento t ON t.id=r.tipo_evento_id "
            "ORDER BY r.fecha_hora"
        )
        .fetchall()
    )
    return render_template("recordatorios.html", filas=filas)


@app.route("/admin/historial")
@login_requerido
def historial():
    """US-M06-009: últimos 60 días, orden descendente, filtros y email enmascarado."""
    tipo = request.args.get("tipo", "Todos")
    estado = request.args.get("estado", "Todos")
    desde = (ahora() - timedelta(days=60)).isoformat()
    sql = "SELECT * FROM notificacion WHERE enviada_en >= ?"
    params = [desde]
    if tipo != "Todos":
        sql += " AND tipo=?"
        params.append(tipo)
    if estado != "Todos":
        sql += " AND estado=?"
        params.append(estado.lower())
    filas = get_db().execute(sql + " ORDER BY enviada_en DESC, id DESC", params).fetchall()
    if estado != "Todos":
        vacio = f"No se encontraron notificaciones con estado {estado} en los últimos 60 días"
    else:
        vacio = "No se encontraron notificaciones para los filtros seleccionados en los últimos 60 días"
    return render_template(
        "historial.html",
        filas=filas,
        tipo=tipo,
        estado=estado,
        vacio=vacio,
        tipos=["Todos", "Confirmación", "Recordatorio", "Cancelación", "Aviso al admin"],
    )


# ---------------------------------------------------------------------------
# ABM de plantillas (M06-R04F: US-M06-004, 005, 006)
# ---------------------------------------------------------------------------
def plantillas_por_tipo():
    db = get_db()
    grupos = []
    for tipo in TIPOS_PLANTILLA:
        filas = db.execute("SELECT * FROM plantilla WHERE tipo=? ORDER BY por_defecto DESC, nombre", (tipo,)).fetchall()
        grupos.append((tipo, filas))
    return grupos


def validar_campos(form, plantilla_id=None):
    errores, avisos = {}, []
    datos = {k: form.get(k, "").strip() for k in ("nombre", "tipo", "asunto", "saludo", "cuerpo", "firma")}
    if not datos["nombre"]:
        errores["nombre"] = "El nombre es obligatorio."
    for campo, limite in LIMITES.items():
        if len(datos[campo]) > limite:
            errores[campo] = f"Máximo {limite} caracteres ({len(datos[campo])} ingresados)."
    duplicada = (
        get_db()
        .execute("SELECT id FROM plantilla WHERE lower(trim(nombre))=lower(trim(?))", (datos["nombre"],))
        .fetchone()
    )
    if duplicada and duplicada["id"] != plantilla_id:
        errores["nombre"] = MSG_NOMBRE_DUPLICADO  # US-M06-004, Escenario 4
    for campo in ("asunto", "saludo", "cuerpo", "firma"):
        if not datos[campo] and not errores:
            datos[campo] = TEXTOS_POR_DEFECTO[campo]
            avisos.append(f"El campo {campo.capitalize()} estaba vacío. Se usó el texto por defecto.")
    return datos, errores, avisos


@app.route("/admin/plantillas")
@login_requerido
def plantillas():
    return render_template("plantillas.html", grupos=plantillas_por_tipo())


@app.route("/admin/plantillas/nueva", methods=["GET", "POST"])
@login_requerido
def plantilla_nueva():
    db = get_db()
    datos, errores = {"tipo": TIPOS_PLANTILLA[0]}, {}
    if request.method == "POST":
        datos, errores, avisos = validar_campos(request.form)
        if datos["tipo"] not in TIPOS_PLANTILLA:
            errores["tipo"] = "Tipo inválido."
        if not errores:
            existentes = db.execute("SELECT COUNT(*) FROM plantilla WHERE tipo=?", (datos["tipo"],)).fetchone()[0]
            tick = request.form.get("por_defecto") == "on"
            por_defecto = 1 if (existentes == 0 or tick) else 0  # primera del tipo => por defecto
            if tick and existentes > 0:
                db.execute("UPDATE plantilla SET por_defecto=0 WHERE tipo=?", (datos["tipo"],))
                avisos.append("★ Esta plantilla es ahora la por defecto. La anterior quedó como alternativa.")
            db.execute(
                "INSERT INTO plantilla (nombre, tipo, asunto, saludo, cuerpo, firma, por_defecto, autor, creada_en) "
                "VALUES (?,?,?,?,?,?,?,?,?)",
                (
                    datos["nombre"],
                    datos["tipo"],
                    datos["asunto"],
                    datos["saludo"],
                    datos["cuerpo"],
                    datos["firma"],
                    por_defecto,
                    session["admin"],
                    ahora().isoformat(),
                ),
            )
            flash("Plantilla creada correctamente")
            for a in avisos:
                flash(a)
            return redirect(url_for("plantillas"))
    return render_template(
        "plantilla_form.html", datos=datos, errores=errores, tipos=TIPOS_PLANTILLA, modo="nueva", limites=LIMITES
    )


@app.route("/admin/plantillas/<int:pid>/editar", methods=["GET", "POST"])
@login_requerido
def plantilla_editar(pid):
    db = get_db()
    p = db.execute("SELECT * FROM plantilla WHERE id=?", (pid,)).fetchone() or abort(404)
    datos, errores, preview = dict(p), {}, None
    if request.method == "POST":
        form = request.form.to_dict()
        form["tipo"] = p["tipo"]  # el tipo no es editable
        datos, errores, avisos = validar_campos(form, plantilla_id=pid)
        datos["por_defecto"] = 1 if request.form.get("por_defecto") == "on" else 0
        datos["id"] = pid
        if request.form.get("accion") == "preview" and not errores:
            ejemplo = {
                "nombre_invitado": "María García",
                "nombre_profesional": "Dr. García",
                "fecha_turno": "miércoles 18 de noviembre de 2026",
                "hora_turno": "10:30",
                "fecha_corta": "18/11/2026",
                "tipo_evento": "Consulta inicial - 30 min",
            }
            preview = {k: completar(datos[k], ejemplo) for k in ("asunto", "saludo", "cuerpo", "firma")}
        elif not errores:
            otras = db.execute(
                "SELECT * FROM plantilla WHERE tipo=? AND id<>? ORDER BY id", (p["tipo"], pid)
            ).fetchall()
            if p["por_defecto"] and not datos["por_defecto"]:
                if not otras:  # US-M06-005, Escenario 4
                    errores["por_defecto"] = MSG_TICK_UNICA
                    return render_template(
                        "plantilla_form.html",
                        datos=datos,
                        errores=errores,
                        tipos=TIPOS_PLANTILLA,
                        modo="editar",
                        limites=LIMITES,
                        preview=None,
                        error_general=MSG_TICK_UNICA,
                    )
                db.execute("UPDATE plantilla SET por_defecto=1 WHERE id=?", (otras[0]["id"],))
                avisos.append(f"'{otras[0]['nombre']}' pasó a ser la plantilla por defecto del tipo.")
            if datos["por_defecto"] and not p["por_defecto"]:
                db.execute("UPDATE plantilla SET por_defecto=0 WHERE tipo=?", (p["tipo"],))
                avisos.append("★ Esta plantilla es ahora la por defecto. La anterior quedó como alternativa.")
            # guardar versión anterior en el historial (máx. 5)
            db.execute(
                "INSERT INTO plantilla_version (plantilla_id, asunto, saludo, cuerpo, firma, guardada_en, autor) "
                "VALUES (?,?,?,?,?,?,?)",
                (
                    pid,
                    p["asunto"],
                    p["saludo"],
                    p["cuerpo"],
                    p["firma"],
                    p["modificada_en"] or p["creada_en"],
                    p["modificada_por"] or p["autor"],
                ),
            )
            db.execute(
                "DELETE FROM plantilla_version WHERE plantilla_id=? AND id NOT IN (SELECT id FROM "
                "plantilla_version WHERE plantilla_id=? ORDER BY id DESC LIMIT ?)",
                (pid, pid, MAX_VERSIONES),
            )
            db.execute(
                "UPDATE plantilla SET nombre=?, asunto=?, saludo=?, cuerpo=?, firma=?, por_defecto=?, "
                "modificada_por=?, modificada_en=? WHERE id=?",
                (
                    datos["nombre"],
                    datos["asunto"],
                    datos["saludo"],
                    datos["cuerpo"],
                    datos["firma"],
                    datos["por_defecto"],
                    session["admin"],
                    ahora().isoformat(),
                    pid,
                ),
            )
            flash("Plantilla actualizada correctamente")
            for a in avisos:
                flash(a)
            return redirect(url_for("plantillas"))
    return render_template(
        "plantilla_form.html",
        datos=datos,
        errores=errores,
        tipos=TIPOS_PLANTILLA,
        modo="editar",
        limites=LIMITES,
        preview=preview,
    )


@app.route("/admin/plantillas/<int:pid>/historial")
@login_requerido
def plantilla_historial(pid):
    db = get_db()
    p = db.execute("SELECT * FROM plantilla WHERE id=?", (pid,)).fetchone() or abort(404)
    versiones = db.execute("SELECT * FROM plantilla_version WHERE plantilla_id=? ORDER BY id DESC", (pid,)).fetchall()
    return render_template("plantilla_historial.html", p=p, versiones=versiones)


@app.route("/admin/plantillas/<int:pid>/restaurar/<int:vid>", methods=["POST"])
@login_requerido
def plantilla_restaurar(pid, vid):
    db = get_db()
    p = db.execute("SELECT * FROM plantilla WHERE id=?", (pid,)).fetchone() or abort(404)
    v = db.execute("SELECT * FROM plantilla_version WHERE id=? AND plantilla_id=?", (vid, pid)).fetchone() or abort(404)
    db.execute(
        "INSERT INTO plantilla_version (plantilla_id, asunto, saludo, cuerpo, firma, guardada_en, autor) "
        "VALUES (?,?,?,?,?,?,?)",
        (
            pid,
            p["asunto"],
            p["saludo"],
            p["cuerpo"],
            p["firma"],
            p["modificada_en"] or p["creada_en"],
            p["modificada_por"] or p["autor"],
        ),
    )
    db.execute(
        "UPDATE plantilla SET asunto=?, saludo=?, cuerpo=?, firma=?, modificada_por=?, modificada_en=? WHERE id=?",
        (v["asunto"], v["saludo"], v["cuerpo"], v["firma"], session["admin"], ahora().isoformat(), pid),
    )
    flash("Versión restaurada correctamente")
    return redirect(url_for("plantilla_historial", pid=pid))


@app.route("/admin/plantillas/<int:pid>/eliminar", methods=["POST"])
@login_requerido
def plantilla_eliminar(pid):
    """US-M06-006. La eliminación es definitiva; el historial de envíos se conserva."""
    db = get_db()
    p = db.execute("SELECT * FROM plantilla WHERE id=?", (pid,)).fetchone() or abort(404)
    del_tipo = db.execute("SELECT COUNT(*) FROM plantilla WHERE tipo=?", (p["tipo"],)).fetchone()[0]
    if del_tipo == 1:
        flash(MSG_ELIMINAR_UNICA, "error")
    elif p["por_defecto"]:
        flash(MSG_ELIMINAR_DEFECTO, "error")
    else:
        db.execute("DELETE FROM plantilla WHERE id=?", (pid,))
        db.execute("DELETE FROM plantilla_version WHERE plantilla_id=?", (pid,))
        flash("Plantilla eliminada correctamente")
    return redirect(url_for("plantillas"))


# ---------------------------------------------------------------------------
# Buzón de pruebas (reemplaza a Mailtrap)
# ---------------------------------------------------------------------------
@app.route("/buzon")
def buzon():
    email = request.args.get("email", "").strip()
    db = get_db()
    destinatarios = [
        r[0]
        for r in db.execute(
            "SELECT DISTINCT destinatario FROM notificacion WHERE estado='enviado' ORDER BY destinatario"
        )
    ]
    mensajes = []
    if email:
        mensajes = db.execute(
            "SELECT * FROM notificacion WHERE destinatario=? AND estado='enviado' ORDER BY id DESC", (email,)
        ).fetchall()
    return render_template("buzon.html", email=email, mensajes=mensajes, destinatarios=destinatarios)


@app.route("/buzon/<int:nid>")
def buzon_mensaje(nid):
    m = get_db().execute("SELECT * FROM notificacion WHERE id=?", (nid,)).fetchone() or abort(404)
    return render_template("mensaje.html", m=m)


# ---------------------------------------------------------------------------
# Entorno de test: reloj, servicio de correo y preparación de escenarios
# ---------------------------------------------------------------------------
@app.route("/entorno", methods=["GET", "POST"])
def entorno():
    from escenarios import ESCENARIOS

    if request.method == "POST":
        accion = request.form.get("accion")
        if accion == "reloj":
            fijar_reloj(datetime.fromisoformat(request.form["momento"]))
            flash(f"Reloj del entorno fijado en {request.form['momento'].replace('T', ' ')}")
        elif accion == "correo":
            set_cfg("servicio_correo", request.form["estado"])
            flash(f"Servicio de correo: {request.form['estado']}")
        elif accion == "escenario":
            cp = request.form["cp"]
            ESCENARIOS[cp][1]()
            session.clear()
            flash(f"Entorno preparado para {cp}: {ESCENARIOS[cp][0]}")
        return redirect(url_for("entorno"))
    return render_template("entorno.html", escenarios=ESCENARIOS)


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        from escenarios import preparar_base

        with app.app_context():
            preparar_base()
    app.run(debug=True, port=5000)
