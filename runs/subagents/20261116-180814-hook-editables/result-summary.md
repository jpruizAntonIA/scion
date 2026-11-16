# Resultado: ejecutor deskops-e-b43affadd52e (intento 1)

Tarea: task-fase-0-ir-hook-pre-start-deskops-tools-instala-sldb-y-deskops-editables-desde-workspace

## Qué hice
- Verifiqué hooks/pre-start-deskops.sh (main, f6e623c69 + 56a66098c) contra Goal/Scope; no lo modifiqué.
- Creé `tests/test_hook_pre_start_deskops.py` (único archivo nuevo de código, sin commitear): dos tests que corren
  la Validation del contrato con `deskops.testing.foreign_suites.run_foreign_suite` (argv en lista, sin shell en el host):
  - `test_hook_parses`: `bash -n hooks/pre-start-deskops.sh`.
  - `test_hook_installs_editable_tools_in_claude_image`: `timeout 600 docker run --rm --entrypoint bash --user 1001:1003
    -e HOME=/tmp/h -e SCION_WORKSPACE=/workspace -v <workspace>:/workspace -v <scion>/hooks/pre-start-deskops.sh:/hook.sh:ro
    ghcr.io/jpruizantonia/scion-claude:f6e623c69 -c "<comando del contrato> && grep -qF <rutas> && deskops --help && sldb --help"`.
    Las afirmaciones van dentro del contenedor (grep -q) para que un fallo sea rc != 0 y el puente decida.
  - Rutas: scion = Path(__file__).resolve().parents[1]; workspace = $SCION_TEST_WORKSPACE o scion.parent.

## Veredicto por validación
| Validación | Resultado |
|---|---|
| `bash -n hooks/pre-start-deskops.sh` | rc 0 |
| pytest del test nuevo (uv run --no-project --with pytest --with-editable /mnt/ssd/herramientas/deskops) | rc 0, 2 passed (pytest.out) |
| docker run exacto del contrato (manual, salida en docker-run.out) | rc 0; imprime `/workspace/deskops/deskops/__init__.py /workspace/sldb/src/sldb/__init__.py`; `deskops --help` y `sldb --help` corren |
| Workspace limpio: `git status --short` de sldb y deskops antes/después | sin diferencias (archivos *-status-before/after.txt) |
| `git check-ignore` de los egg-info | sldb `src/structuredLanguageDB.egg-info` (.gitignore:19) y deskops `deskops.egg-info` (.gitignore:8): ignorados |

## Hook vs contrato
Cumple: `uv tool install --quiet --python $PYTHON_SPEC --reinstall --editable` para sldb y para deskops con
`--with-editable $SLDB_SRC`; WORKSPACE=${SCION_WORKSPACE:-/workspace}; PYTHON_SPEC=${DESKOPS_PYTHON:-3.13};
uv propio vía curl/wget (sin ninguno, exit 1); exit 1 si falta algún pyproject.toml; exit 1 si faltan los
ejecutables en $HOME/.local/bin; PATH en .profile/.bashrc; ningún .gitignore tocado.
Observaciones (no bloqueantes, no corregidas):
- El hook tiene además el bloque de re-ejecución como usuario cuando corre como root y el venv de test
  (56a66098c), fuera del Scope de esta tarea; en la validación (uid 1001, DESKOPS_DESK_ROOT vacío) no se ejercitan
  ("skipping test venv").
- La línea final de log reporta `python /workspace/.venv/bin/python`: `uv python find 3.13` encuentra el .venv del
  workspace (cwd del contenedor), no el Python de las herramientas. Solo cosmético en el log.

## Para el supervisor
- Archivo a integrar: tests/test_hook_pre_start_deskops.py. tests/test_go_build_context_suite.py es del otro ejecutor.
- Borré solo mi .pyc de tests/__pycache__; el del otro ejecutor sigue ahí.
- No commiteé ni cerré la tarea; no toqué desk/ ni .sldb/.
