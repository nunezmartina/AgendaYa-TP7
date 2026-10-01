// AgendaYA — Frontend mínimo del módulo M06 (Notificaciones)
// Datos en memoria (sin backend real, según lo permitido por la consigna del TP6).

// --- Lógica de negocio (misma lógica que en src/logica-negocio.js) ---------
function esEmailValido(email) {
  if (typeof email !== 'string' || email.trim() === '') return false;
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email.trim());
}

function calcularEsPorDefecto({ existeOtraPlantillaDelTipo, tickActivado }) {
  if (!existeOtraPlantillaDelTipo) return true;
  return !!tickActivado;
}

// --- Estado en memoria -------------------------------------------------
const plantillas = []; // { nombre, tipo, asunto, saludo, cuerpo, firma, porDefecto }
const historial = [];  // { tipo, email, estado }

// --- Navegación por tabs -------------------------------------------------
document.querySelectorAll('.tab-btn').forEach((btn) => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach((b) => b.classList.remove('active'));
    document.querySelectorAll('.vista').forEach((v) => v.classList.add('oculto'));
    btn.classList.add('active');
    document.getElementById(btn.dataset.target).classList.remove('oculto');
  });
});

// --- FLUJO 1: Configurar plantilla de email -------------------------------
const formPlantilla = document.getElementById('form-plantilla');
const errorCampoVacio = document.querySelector('[data-cy="error-campo-vacio"]');
const errorNombreDuplicado = document.querySelector('[data-cy="error-nombre-duplicado"]');
const plantillaCreadaOk = document.querySelector('[data-cy="plantilla-creada-confirmacion"]');
const listaPlantillas = document.getElementById('lista-plantillas');

function renderPlantillas() {
  listaPlantillas.innerHTML = '';
  plantillas.forEach((p) => {
    const li = document.createElement('li');
    li.setAttribute('data-cy', 'plantilla-item');
    li.textContent = `${p.porDefecto ? '★ ' : ''}${p.nombre} — ${p.tipo}`;
    if (p.porDefecto) li.classList.add('estrella');
    listaPlantillas.appendChild(li);
  });
}

formPlantilla.addEventListener('submit', (e) => {
  e.preventDefault();
  errorCampoVacio.classList.add('oculto');
  errorNombreDuplicado.classList.add('oculto');
  plantillaCreadaOk.classList.add('oculto');

  const nombre = document.getElementById('nombre-input').value.trim();
  const tipo = document.getElementById('tipo-select').value;
  const asunto = document.getElementById('asunto-input').value.trim();
  const saludo = document.getElementById('saludo-input').value.trim();
  const cuerpo = document.getElementById('cuerpo-input').value.trim();
  const firma = document.getElementById('firma-input').value.trim();
  const tickActivado = document.getElementById('por-defecto-checkbox').checked;

  // Validación: campo vacío
  if (!nombre || !asunto || !saludo || !cuerpo || !firma) {
    errorCampoVacio.classList.remove('oculto');
    return;
  }

  // Validación: nombre único
  const existeNombre = plantillas.some((p) => p.nombre.toLowerCase() === nombre.toLowerCase());
  if (existeNombre) {
    errorNombreDuplicado.classList.remove('oculto');
    return;
  }

  const existeOtraPlantillaDelTipo = plantillas.some((p) => p.tipo === tipo);
  const esPorDefecto = calcularEsPorDefecto({ existeOtraPlantillaDelTipo, tickActivado });

  if (esPorDefecto) {
    // Desplaza a la anterior por defecto del mismo tipo
    plantillas.forEach((p) => {
      if (p.tipo === tipo) p.porDefecto = false;
    });
  }

  plantillas.push({ nombre, tipo, asunto, saludo, cuerpo, firma, porDefecto: esPorDefecto });

  renderPlantillas();
  plantillaCreadaOk.classList.remove('oculto');
  formPlantilla.reset();
});

// --- FLUJO 2: Simular envío de notificación -------------------------------
const formSimular = document.getElementById('form-simular');
const errorEmailInvalido = document.querySelector('[data-cy="error-email-invalido"]');
const errorEnvioFallido = document.querySelector('[data-cy="error-envio-fallido"]');
const notificacionEnviadaOk = document.querySelector('[data-cy="notificacion-enviada-confirmacion"]');
const historialEnvios = document.getElementById('historial-envios');

function renderHistorial() {
  historialEnvios.innerHTML = '';
  historial.forEach((h) => {
    const li = document.createElement('li');
    li.setAttribute('data-cy', 'historial-item');
    li.textContent = `${h.tipo} → ${h.email} (${h.estado})`;
    historialEnvios.appendChild(li);
  });
}

formSimular.addEventListener('submit', (e) => {
  e.preventDefault();
  errorEmailInvalido.classList.add('oculto');
  errorEnvioFallido.classList.add('oculto');
  notificacionEnviadaOk.classList.add('oculto');

  const tipo = document.getElementById('tipo-notificacion-select').value;
  const email = document.getElementById('email-destinatario-input').value.trim();
  const simularFallo = document.getElementById('simular-fallo-checkbox').checked;

  if (!esEmailValido(email)) {
    errorEmailInvalido.classList.remove('oculto');
    return;
  }

  if (simularFallo) {
    errorEnvioFallido.classList.remove('oculto');
    historial.push({ tipo, email, estado: 'fallido' });
    renderHistorial();
    return;
  }

  historial.push({ tipo, email, estado: 'enviado' });
  renderHistorial();
  notificacionEnviadaOk.classList.remove('oculto');
  formSimular.reset();
});
