# AgendaYA – Módulo M06 Notificaciones y Comunicaciones

Trabajo Práctico N°5 – Casos de Prueba · Ingeniería y Calidad de Software · Grupo 9

Implementación mínima del módulo M06 para poder ejecutar los 16 casos de prueba del TP
(8 positivos y 8 negativos). No es el sistema completo: incluye solo lo que cubren los CP.

## Qué incluye

| Funcionalidad | Requerimiento | Casos de prueba |
| --- | --- | --- |
| Reserva pública con validación de email y email de confirmación | M06-R01F, M06-R01NF | CP-001, CP-002 |
| Aviso al administrador (email + alerta en el panel en tiempo real) | M06-R02F | CP-003, CP-004 |
| Recordatorio automático 24 hs antes (scheduler con reloj simulado) | M06-R03F | CP-005, CP-006 |
| ABM de plantillas con "Por defecto", versiones y restricciones | M06-R04F | CP-007 a CP-012 |
| Cancelación por el admin con motivo y toggle de notificación | M06-R05F | CP-013 a CP-015 |
| Historial de notificaciones con filtros y emails enmascarados | M06-R02F (US-M06-009) | CP-016 |

Los emails no se envían a un servidor real: quedan en un **buzón de pruebas** (`/buzon`),
como haría Mailtrap (ver M06-R06NF del TP1).

## Cómo correrlo

Requiere Python 3.10 o superior.

```bash
python -m venv venv
source venv/bin/activate        # en Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abrir http://localhost:5000

- Administrador: `admin@agendaya.com` / `Admin1234!`
- **Entorno de test** (`/entorno`): botón "Preparar" para cargar los prerrequisitos de cada CP,
  reloj simulado y simulación de caída del servicio de correo.

## Tests automatizados

Hay un test por cada caso de prueba (`tests/test_casos_de_prueba.py`), nombrado con su identificador:

```bash
python -m pytest -v
```

## Estructura

```
app.py              rutas y reglas de negocio del módulo M06
escenarios.py       datos semilla y prerrequisitos de cada CP
templates/          pantallas (Jinja2)
static/estilos.css  estilos
tests/              un test automatizado por CP
```
