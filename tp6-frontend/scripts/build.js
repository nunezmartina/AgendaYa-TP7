// Build del frontend (TP7): valida y empaqueta frontend/ en dist/ para Firebase Hosting.
// 1) verifica la sintaxis de cada .js sin ejecutarlo
// 2) verifica que existan los recursos que referencia index.html
// 3) copia el resultado a dist/ (lo que usan los tests E2E y los despliegues)
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const origen = path.join(__dirname, '..', 'frontend');
const destino = path.join(__dirname, '..', 'dist');

function fallar(mensaje) {
  console.error(`Build fallido: ${mensaje}`);
  process.exit(1);
}

if (!fs.existsSync(path.join(origen, 'index.html'))) fallar('falta frontend/index.html');

const archivosJs = fs.readdirSync(origen).filter((f) => f.endsWith('.js'));
for (const archivo of archivosJs) {
  const codigo = fs.readFileSync(path.join(origen, archivo), 'utf8');
  try {
    new vm.Script(codigo, { filename: archivo });
  } catch (error) {
    fallar(`error de sintaxis en ${archivo}: ${error.message}`);
  }
}

const html = fs.readFileSync(path.join(origen, 'index.html'), 'utf8');
const referencias = [...html.matchAll(/(?:src|href)="([^"#:]+)"/g)].map((m) => m[1]);
for (const ref of referencias) {
  if (!fs.existsSync(path.join(origen, ref)))
    fallar(`index.html referencia "${ref}", que no existe`);
}

fs.rmSync(destino, { recursive: true, force: true });
fs.cpSync(origen, destino, { recursive: true });

console.log(
  `Build OK: ${archivosJs.length} archivos JS validados, ${referencias.length} recursos verificados, dist/ generado`,
);
