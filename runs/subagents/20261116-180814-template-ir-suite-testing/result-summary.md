# result-summary: tester deskops-t-746aca240a1f-a2 (intento 2)

- Tarea: task-fase-0-ir-template-del-ejecutor-de-ir-con-tmp-en-ram-lock-de-tests-compartido-y-tope-de-memoria
- Rol: tester (role-deskops-tester), subagente local en robocop2; run run-deskops-t-746aca240a1f-a2
- Objeto: tests/test_deskops_ir_template_suite.py (sin commitear, sha256 en test-file.sha256, sin cambios durante la prueba)
- Run del ejecutor: no leído.

| Punto | Resultado | Evidencia |
|---|---|---|
| a) test corrido con el puente en la instalación limpia | PASS: `4 passed in 968.12s`, rc 0 | a-suite.out, validation.log |
| b1) archivos y -k del contrato, sin shell | PASS: test_scion_runtime, test_role_runtime_artifacts, test_command_registry de a uno; test_output_goldens con `-k test_help_goldens` (solo coincide con `def test_help_goldens`, línea 316); argv en listas, run_foreign_suite usa subprocess.run sin shell | revisión del código |
| b2) la comprobación de ancestros falla de verdad | PASS: `0000000` -> exit 128 FAIL; `48f4aef8` (commit existente no ancestro de HEAD) -> exit 1 FAIL; `4a7707a5` -> PASS. Los 3 commits del contrato son ancestros de HEAD 339bacca. Fixture autouse de módulo: si falla, falla toda la suite | b-ancestor-negative.out (el .py temporal en /dev/shm fue borrado) |
| b3) usa la instalación limpia, no SLDB_1/deskops | PASS: DESKOPS=/mnt/ssd/herramientas/deskops, SLDB=/mnt/ssd/herramientas/sldb por defecto; no hay referencia a /mnt/ssd/proyectos/SLDB_1/deskops | revisión del código |
| c) instalaciones sin cambios | PASS: status vacío y mismo HEAD (deskops 339bacca, sldb b60b02b7) antes y después | install-status-{before,after}.txt |
| /dev/shm | sin tmp* nuevos de esta corrida | devshm-tmp-{before,after}.txt |

Global: PASS

Observaciones (no bloqueantes):
- Las rutas se pueden sobreescribir con DESKOPS_TEST_CHECKOUT / SLDB_TEST_CHECKOUT; por defecto usan la instalación limpia.
- `env.setdefault("TMPDIR", "/dev/shm")`: si quien lo corre ya tiene otro TMPDIR, se respeta en vez de forzar /dev/shm.
- Tardó 16 min (no 13); los timeouts por archivo (600 s, 1200 s para goldens) alcanzaron.
- Las validaciones 3 y 4 (medición de fsync, lock) no son parte de esta prueba; su evidencia está en los runs -testing y -lock-testing.
