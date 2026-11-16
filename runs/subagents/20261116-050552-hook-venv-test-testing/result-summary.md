# result-summary — run-deskops-t-df963d64464a (tester, intento 1)

- Tarea: task-hook-deskops-tools-venv-de-test-del-repo-de-la-tarea-pytest-pytest-xdist-y-extras-de-test-dentro-del
- Rol: tester (role-deskops-tester), runtime claude en herdr/robocop2
- Objeto probado: diff sin commitear de `hooks/pre-start-deskops.sh` (un solo hunk `@@ -76,6 +76,45 @@`, solo líneas añadidas)
- Evidencia: `validation.log` (comando + rc de cada corrida), salidas en `v1.out`, `v2.out`, `v3.out`,
  `neg-baddep.out`, `neg-badtoml.out`, `extra-root.out`, `extra-symlink.out`, `ir-status-{before,after,diff}.txt`,
  `ir-newer-than-start.txt`. El run del ejecutor lo leí recién después de terminar mis pruebas.

## Veredicto global: **PASS**

## Validaciones del contrato

| # | Validación | rc | Veredicto |
|---|---|---|---|
| V1 | `bash -n hooks/pre-start-deskops.sh` | 0 | PASS |
| V2 | docker run con `DESKOPS_DESK_ROOT=/mnt/ssd/proyectos/SLDB_1/IR`: hook + `pytest -q -n 2 -p no:cacheprovider tests/test_imports.py` + `task-python -c 'import xdist, sldb, yaml; print(sldb.__file__)'` | 0 | PASS: log `extra: test`, xdist levantó 2 workers, `9 passed in 0.95s`, imprime `/mnt/ssd/proyectos/SLDB_1/sldb/src/sldb/__init__.py` |
| V3 | mismo docker run con `DESKOPS_DESK_ROOT=` (vacío), solo el hook | 0 | PASS: log `skipping test venv: DESKOPS_DESK_ROOT='' has no pyproject.toml`, termina en `ready`; no se crea `/tmp/h/.venvs/task` ni `pytest`/`task-python` en `.local/bin` (añadí `ls` al final del comando, conservando el rc del hook) |
| V4 | `git -C IR status --short` sin archivos nuevos tras las corridas | — | PASS (con hallazgo H1): las entradas nuevas del diff before/after son todas actividad ajena (desk/inbox, `.sldb/core/...InboxNoteDoc`, ReviewDoc `ir13e...bundle-1`, `runs/subagents/20261116-051139/`: otro agente revisando ir13e y la nota de inbox de scion). Ninguna entrada nueva atribuible al hook. |

## Salvaguardas pedidas

- **Salto con DESKOPS_DESK_ROOT vacío → rc 0**: PASS (V3).
- **exit 1 si la instalación falla**: PASS, dos casos en un dir temporal `/dev/shm/hookneg.*` (borrado después; verificado que no queda):
  - pyproject válido con dependencia inexistente (`no-such-package-zzz-hookneg==9.9.9`, extra `dev`): rc 1, log `test venv install failed for .../baddep[dev] in /tmp/h/.venvs/task`. Confirma además el fallback a `dev`.
  - pyproject TOML inválido: rc 1, log `cannot read .../pyproject.toml to pick the test extra`.
- **IR sin archivos nuevos por el hook**: PASS en el estado actual de IR; ver H1.
- **Resto del hook igual (runuser, uv, PYTHON_SPEC)**: PASS. El diff es una sola inserción entre el chequeo de sldb/deskops en `$TOOL_BIN` y el bloque PATH/rc + `ready`; cero líneas borradas o modificadas. Prueba extra (`extra-root.out`, rc 0): como root con `scion` remapeado a uid 1001 dentro del contenedor efímero, el re-exec por `runuser` hereda `DESKOPS_DESK_ROOT` (crea el venv con `extra: test`), venv y enlaces quedan con dueño `scion`, root sigue creando solo `/usr/local/bin/{sldb,deskops}`, y `runuser -u scion -- task-python -c 'import xdist, sldb, specir'` funciona.

## Nota task-python (wrapper sh en vez de symlink)

Comprobado empíricamente (`extra-symlink.out`, misma imagen, sin tocar el workspace): un symlink a `venv/bin/python` desde
otro directorio da `sys.prefix=/usr`, fuera del venv; el wrapper `exec venv/bin/python "$@"` da `sys.prefix=/tmp/h/v`,
dentro del venv. El contrato pedía literalmente `ln -sf ... task-python`, pero su objetivo ("task-python apunta a ese venv"
y que el import de xdist/sldb/yaml funcione) solo se cumple con el wrapper; el symlink lo rompería. **Cumple el objetivo;
desviación justificada.** `pytest` sí es symlink y funciona porque su shebang apunta al python del venv.

## Hallazgos

- **H1 (no bloqueante para esta tarea, ya derivado):** la premisa del contrato "esos repos ignoran *.egg-info en .gitignore"
  es falsa para IR: `IR/.gitignore` solo ignora `.sldb_cache/`, `.deskops.log` y `runs/subagents/*/session.jsonl`
  (`git check-ignore` rc 1 para `src/specir.egg-info` y `tests/__pycache__`). V4 pasa solo porque `src/specir.egg-info/`
  ya estaba sin trackear desde 2026-11-15 18:01 (-03), antes de esta tarea; el hook lo reescribe (mtime de `PKG-INFO`
  dentro de mis corridas). En un checkout limpio de IR el hook dejaría `?? src/specir.egg-info/` (y pytest, `__pycache__/`).
  sldb sí lo ignora (`.gitignore:19:*.egg-info/`). Ya existe la nota `IR/desk/inbox/20261116-021128-suggestion-ir-gitignore-no-ignora-egg-info-ni-pycache-el-hook-de-scion-instala-ir-editable.md` pidiendo agregar `*.egg-info/` y `__pycache__/` a IR/.gitignore: es el seguimiento correcto, fuera del alcance de esta tarea.
- **H2 (menor):** el comentario del bloque dice "nothing else is written into the task repo"; correr pytest escribe `__pycache__/`
  en IR (no lo escribe el hook en sí). Sin acción para esta tarea.
- **H3 (menor):** el run del ejecutor registra una primera corrida V2 con rc 1 antes de la corrida en verde; no afecta mi
  evidencia, que es propia y en verde al primer intento.
- Done When exige además el hook **commiteado en main**: hoy está sin commitear (lo cierra el coordinador).

## Tests faltantes / stale

Ninguno en el repo: el contrato valida por docker run, no hay tests unitarios del hook. No corrí suites completas.

## Limpieza

Sin cambios fuera del run_dir; nada en `/dev/shm` de mis corridas (dir `hookneg.*` borrado); contenedores con `--rm`.
