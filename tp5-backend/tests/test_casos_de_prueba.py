"""Un test automatizado por cada caso de prueba del TP N°5 (Grupo 9)."""
from conftest import login, fijar_reloj, bandeja, query

TURNO = "2026-11-18T10:30:00"
RESERVAR = f"/agenda/dr-garcia/1/reservar?fh={TURNO}"


def reservar(client, nombre, email, telefono="", nota="", fh=TURNO, evento=1):
    return client.post(f"/agenda/dr-garcia/{evento}/reservar?fh={fh}",
                       data={"nombre": nombre, "email": email, "telefono": telefono, "nota": nota},
                       follow_redirects=True)


# ---------------------------------------------------------------- M06-R01F
def test_CP_001_email_de_confirmacion_con_email_valido(preparar):
    c = preparar("CP-001")
    r = reservar(c, "María García", "maria.garcia@gmail.com")
    html = r.get_data(as_text=True)
    assert "¡Reserva confirmada! Te enviamos un email de confirmación a maria.garcia@gmail.com" in html
    envio = query("SELECT * FROM notificacion WHERE destinatario='maria.garcia@gmail.com'")[0]
    reserva = query("SELECT * FROM reserva WHERE invitado_email='maria.garcia@gmail.com'")[0]
    assert envio["estado"] == "enviado" and envio["plantilla_nombre"] == "Confirmación formal"
    assert envio["asunto"] == "Tu reserva con Dr. García está confirmada"
    from datetime import datetime
    demora = datetime.fromisoformat(envio["enviada_en"]) - datetime.fromisoformat(reserva["creada_en"])
    assert demora.total_seconds() < 30  # M06-R01NF
    for dato in ("Consulta inicial - 30 min", "miércoles 18 de noviembre de 2026", "10:30",
                 "Presencial", "Av. San Martín 420, Mendoza", "261-555-0001", "Ver detalles de mi reserva"):
        assert dato in envio["cuerpo_html"]


def test_CP_002_email_con_formato_invalido(preparar):
    c = preparar("CP-002")
    html = reservar(c, "María García", "maria.garcia@", telefono="261-555-1234").get_data(as_text=True)
    assert "El email ingresado no es válido. Ej: usuario@dominio.com" in html
    assert query("SELECT COUNT(*) FROM reserva")[0][0] == 0
    assert query("SELECT COUNT(*) FROM notificacion")[0][0] == 0
    assert "10:30" in c.get("/agenda/dr-garcia/1").get_data(as_text=True)  # turno sigue libre


# ---------------------------------------------------------------- M06-R02F
def test_CP_003_notificacion_al_admin_por_nueva_reserva(preparar):
    c = preparar("CP-003")
    reservar(c, "María Gómez", "maria@email.com", "261-555-9999",
             "Primera consulta, vengo derivada del Dr. López")
    login(c)
    assert c.get("/admin/api/alertas").get_json()["badge"] == 1
    html = bandeja(c, "admin@agendaya.com")
    assert "Nueva reserva — María Gómez — 18/11/2026 10:30 hs" in html
    cuerpo = query("SELECT cuerpo_html FROM notificacion WHERE destinatario='admin@agendaya.com'")[0][0]
    for dato in ("María Gómez", "maria@email.com", "261-555-9999", "Consulta inicial - 30 min",
                 "18/11/2026", "10:30", "Primera consulta, vengo derivada del Dr. López"):
        assert dato in cuerpo


def test_CP_004_admin_no_recibe_notificacion_al_cancelar(preparar):
    c = preparar("CP-004")
    login(c)
    assert c.get("/admin/api/alertas").get_json()["badge"] == 0
    c.post("/admin/reservas/1042/cancelar", data={"motivo": "", "notificar": "on"})
    assert query("SELECT estado FROM reserva WHERE id=1042")[0][0] == "Cancelada"
    assert c.get("/admin/api/alertas").get_json()["badge"] == 0
    assert "La bandeja de admin@agendaya.com está vacía" in bandeja(c, "admin@agendaya.com")
    assert "Tu turno con Dr. García fue cancelado" in bandeja(c, "maria@email.com")


# ---------------------------------------------------------------- M06-R03F
def test_CP_005_recordatorio_24_horas_antes(preparar):
    c = preparar("CP-005")
    login(c)
    fijar_reloj(c, "2026-11-17T10:30")
    c.post("/admin/recordatorios")
    r = query("SELECT * FROM reserva WHERE invitado_email='marta@email.com'")[0]
    assert r["recordatorio_estado"] == "enviado" and r["recordatorio_enviado_en"]
    envio = query("SELECT * FROM notificacion WHERE tipo='Recordatorio'")[0]
    assert envio["asunto"] == "Recordatorio: tu turno con Dr. García es mañana"
    assert envio["plantilla_nombre"] == "Recordatorio estándar"
    for dato in ("Consulta inicial - 30 min", "miércoles 18 de noviembre de 2026", "10:30 hs (ARG)",
                 "Presencial", "Av. San Martín 420, Mendoza", "261-555-0001"):
        assert dato in envio["cuerpo_html"]


def test_CP_006_no_se_programa_recordatorio_de_ultimo_momento(preparar):
    c = preparar("CP-006")
    reservar(c, "Pedro Sosa", "pedro@email.com", fh="2026-11-17T20:00:00")
    assert query("SELECT recordatorio_estado FROM reserva")[0][0] == "no aplica"
    fijar_reloj(c, "2026-11-17T19:59")
    login(c)
    c.post("/admin/recordatorios")
    asuntos = [f["asunto"] for f in query("SELECT asunto FROM notificacion WHERE destinatario='pedro@email.com'")]
    assert asuntos == ["Tu reserva con Dr. García está confirmada"]


# ---------------------------------------------------------------- M06-R04F
def test_CP_007_primera_plantilla_del_tipo_queda_por_defecto(preparar):
    c = preparar("CP-007")
    login(c)
    r = c.post("/admin/plantillas/nueva", follow_redirects=True, data={
        "nombre": "Recordatorio verano", "tipo": "Recordatorio al invitado",
        "asunto": "Tu turno con {nombre_profesional} es mañana",
        "saludo": "Hola {nombre_invitado}, te recordamos tu turno de mañana.",
        "cuerpo": "Por favor llegá 5 minutos antes. Ante cualquier consulta llamá al 261-555-0001.",
        "firma": "Dr. García - Medicina General - Tel 261-555-0001"})  # tick NO activado
    assert "Plantilla creada correctamente" in r.get_data(as_text=True)
    p = query("SELECT * FROM plantilla WHERE nombre='Recordatorio verano'")[0]
    assert p["por_defecto"] == 1 and p["autor"] == "admin@agendaya.com" and p["creada_en"]


def test_CP_008_nombre_duplicado(preparar):
    c = preparar("CP-008")
    login(c)
    html = c.post("/admin/plantillas/nueva", data={
        "nombre": "Confirmación formal", "tipo": "Confirmación al invitado",
        "asunto": "Tu reserva con {nombre_profesional} está confirmada", "saludo": "Hola {nombre_invitado}",
        "cuerpo": "Te esperamos.", "firma": "Dr. García"}).get_data(as_text=True)
    assert "Ya existe una plantilla con ese nombre. Por favor usá un nombre diferente" in html
    assert query("SELECT COUNT(*) FROM plantilla WHERE nombre='Confirmación formal'")[0][0] == 1


def _pid(nombre):
    return query("SELECT id FROM plantilla WHERE nombre=?", nombre)[0][0]


def test_CP_009_edicion_conserva_por_defecto(preparar):
    c = preparar("CP-009")
    login(c)
    pid = _pid("Confirmación formal")
    r = c.post(f"/admin/plantillas/{pid}/editar", follow_redirects=True, data={
        "nombre": "Confirmación formal", "asunto": "¡Listo! Tu reserva con {nombre_profesional} está confirmada",
        "saludo": "Hola {nombre_invitado},",
        "cuerpo": "Por favor llegá 5 minutos antes. Ante cualquier consulta llamá al 261-555-0001. ¡Te esperamos!",
        "firma": "Dr. García - Medicina General - Tel 261-555-0001", "por_defecto": "on", "accion": "guardar"})
    assert "Plantilla actualizada correctamente" in r.get_data(as_text=True)
    p = query("SELECT * FROM plantilla WHERE id=?", pid)[0]
    assert p["por_defecto"] == 1 and p["asunto"].startswith("¡Listo!") and p["modificada_por"]
    versiones = query("SELECT asunto FROM plantilla_version WHERE plantilla_id=?", pid)
    assert "Tu reserva con {nombre_profesional} está confirmada" in [v[0] for v in versiones]


def test_CP_010_no_se_puede_quitar_tick_a_la_unica(preparar):
    c = preparar("CP-010")
    login(c)
    pid = _pid("Cancelación con motivo")
    antes = dict(query("SELECT * FROM plantilla WHERE id=?", pid)[0])
    html = c.post(f"/admin/plantillas/{pid}/editar", data={
        "nombre": antes["nombre"], "asunto": antes["asunto"], "saludo": antes["saludo"],
        "cuerpo": antes["cuerpo"], "firma": antes["firma"], "accion": "guardar"}).get_data(as_text=True)
    assert ("No podés quitar el estado por defecto si es la única plantilla de este tipo. "
            "Creá otra y marcala como por defecto primero.") in html
    assert dict(query("SELECT * FROM plantilla WHERE id=?", pid)[0]) == antes


def test_CP_011_eliminar_plantilla_alternativa(preparar):
    c = preparar("CP-011")
    login(c)
    r = c.post(f"/admin/plantillas/{_pid('Confirmación breve')}/eliminar", follow_redirects=True)
    assert "Plantilla eliminada correctamente" in r.get_data(as_text=True)
    assert not query("SELECT 1 FROM plantilla WHERE nombre='Confirmación breve'")
    assert query("SELECT por_defecto FROM plantilla WHERE nombre='Confirmación formal'")[0][0] == 1
    assert query("SELECT COUNT(*) FROM notificacion WHERE plantilla_nombre='Confirmación breve'")[0][0] == 2


def test_CP_012_no_se_puede_eliminar_la_unica(preparar):
    c = preparar("CP-012")
    login(c)
    html = c.get("/admin/plantillas").get_data(as_text=True)
    assert "No podés eliminar la única plantilla de este tipo. Creá otra antes de eliminar esta." in html
    assert "disabled" in html
    c.post(f"/admin/plantillas/{_pid('Recordatorio estándar')}/eliminar")  # intento forzado
    assert query("SELECT por_defecto FROM plantilla WHERE nombre='Recordatorio estándar'")[0][0] == 1


# ---------------------------------------------------------------- M06-R05F
def test_CP_013_cancelacion_con_motivo_envia_email(preparar):
    c = preparar("CP-013")
    login(c)
    r = c.post("/admin/reservas/1042/cancelar", follow_redirects=True,
               data={"motivo": "Surgió un imprevisto. Disculpá las molestias.", "notificar": "on"})
    assert "Email de cancelación enviado a maria@email.com" in r.get_data(as_text=True)
    reserva = query("SELECT * FROM reserva WHERE id=1042")[0]
    assert reserva["estado"] == "Cancelada" and reserva["recordatorio_estado"] == "cancelado"
    envio = query("SELECT * FROM notificacion WHERE tipo='Cancelación'")[0]
    assert envio["asunto"] == "Tu turno con Dr. García fue cancelado"
    for dato in ("<s>Consulta inicial - 30 min</s>", "miércoles 18 de noviembre de 2026",
                 "Surgió un imprevisto. Disculpá las molestias.", "Reservar nuevo turno"):
        assert dato in envio["cuerpo_html"]
    assert "10:30" in c.get("/agenda/dr-garcia/1").get_data(as_text=True)  # horario liberado


def test_CP_014_toggle_desactivado_no_envia_email(preparar):
    c = preparar("CP-014")
    login(c)
    r = c.post("/admin/reservas/1051/cancelar", follow_redirects=True, data={"motivo": ""})
    assert "Reserva cancelada. Notificación al invitado: desactivada" in r.get_data(as_text=True)
    assert query("SELECT estado FROM reserva WHERE id=1051")[0][0] == "Cancelada"
    assert "La bandeja de carlos.ruiz@email.com está vacía" in bandeja(c, "carlos.ruiz@email.com")


def test_CP_015_reagendar_desde_el_email(preparar):
    c = preparar("CP-015")
    cuerpo = query("SELECT cuerpo_html FROM notificacion WHERE tipo='Cancelación'")[0][0]
    assert "href='/agenda/dr-garcia'" in cuerpo
    assert "Consulta inicial - 30 min" in c.get("/agenda/dr-garcia").get_data(as_text=True)
    r = reservar(c, "María Gómez", "maria@email.com", fh="2026-11-20T11:00:00")
    assert "¡Reserva confirmada!" in r.get_data(as_text=True)
    assert query("SELECT estado FROM reserva WHERE fecha_hora='2026-11-20T11:00:00'")[0][0] == "Confirmada"


# ---------------------------------------------------------------- US-M06-009
def test_CP_016_filtro_fallido_sin_resultados(preparar):
    c = preparar("CP-016")
    login(c)
    todos = c.get("/admin/historial").get_data(as_text=True)
    assert todos.count("<td>ma***@email.com</td>") == 1 and "pe***@email.com" in todos and "ca***@email.com" in todos
    assert todos.index("ca***") < todos.index("pe***") < todos.index("ma***")  # orden descendente
    fallido = c.get("/admin/historial?tipo=Todos&estado=Fallido").get_data(as_text=True)
    assert "No se encontraron notificaciones con estado Fallido en los últimos 60 días" in fallido
    assert "enviado</span>" not in fallido
