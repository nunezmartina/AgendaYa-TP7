import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["AGENDAYA_DB"] = os.path.join(tempfile.mkdtemp(), "test.db")

from app import app as flask_app  # noqa: E402
import escenarios  # noqa: E402


@pytest.fixture
def preparar():
    """Prepara el entorno de un CP y devuelve un cliente HTTP."""

    def _preparar(cp):
        with flask_app.app_context():
            escenarios.ESCENARIOS[cp][1]()
        return flask_app.test_client()

    return _preparar


def login(client):
    client.post("/login", data={"email": "admin@agendaya.com", "password": "Admin1234!"})


def fijar_reloj(client, momento):
    client.post("/entorno", data={"accion": "reloj", "momento": momento})


def bandeja(client, email):
    return client.get(f"/buzon?email={email}").get_data(as_text=True)


def query(sql, *params):
    import sqlite3

    db = sqlite3.connect(os.environ["AGENDAYA_DB"])
    db.row_factory = sqlite3.Row
    filas = db.execute(sql, params).fetchall()
    db.close()
    return filas
