## Ticket / incidente
<!-- Ej.: INC-0612 · link al Issue -->

## Causa raíz
<!-- Descripción del problema y por qué se crea este PR -->

## Solución implementada

## Pruebas ejecutadas y pasos para realizar el testing

## Riesgos potenciales

---

### Checklist de revisión (hotfix)
- [ ] El cambio se limita al incidente (sin refactors ni funcionalidades nuevas)
- [ ] Existe un test que reproduce el defecto: falla sin el fix y pasa con el fix
- [ ] El pipeline está en verde (formato, linter, build, tests unitarios y E2E)
- [ ] No se modificaron tests existentes para hacerlos pasar
- [ ] La descripción del PR está completa
- [ ] Está abierto (o se abrirá al mergear) el PR de back-merge `hotfix/*` → `develop`

> Aprobaciones requeridas en `main`: 2 (Tech Lead o desarrollador que no participó del fix + QA Lead).
> El autor no puede aprobar su propio PR.
