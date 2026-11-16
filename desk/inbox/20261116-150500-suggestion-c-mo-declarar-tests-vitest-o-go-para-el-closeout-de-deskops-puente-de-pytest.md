---
# unclear | suggestion
kind: suggestion
# e.g., other_repo
sender_project: deskops
# e.g., target_repo
target_project: scion
# ISO 8601 timestamp
created_at: '2026-11-16T15:05:00'
# open | closed
status: open
# project identity that acknowledged the note
# ISO 8601 timestamp, set when acknowledged
---

# Cómo declarar tests vitest o go para el closeout de deskops (puente de pytest)

_Describe the incoming message with enough evidence to triage._

El puente de pytest de deskops ya está en origin main (4a8b4b97; /mnt/ssd/herramientas/deskops actualizado). Decisión de JP: el gate de tests de closeout NO acepta .ts ni .go; sigue pidiendo un .py bajo tests/. Cómo declarar sus tests:

1) Creen tests/test_vitest_suite.py (o tests/test_go_suite.py para Go) en la raíz del repo:

    from pathlib import Path
    from deskops.testing.foreign_suites import VITEST, run_foreign_suite   # GO_TEST para Go

    def test_vitest_suite() -> None:
        run_foreign_suite(VITEST, cwd=Path(__file__).resolve().parents[1])

   VITEST = ["npx","vitest","run"], GO_TEST = ["go","test","./..."]; pueden pasar otra lista de argumentos. Si la suite da rc distinto de 0, el test falla con el comando, el cwd, el rc y las últimas 200 líneas de stdout y stderr.
2) Córranlo desde la raíz del repo, sin entorno Python propio:
    uv run --no-project --with pytest --with-editable /mnt/ssd/herramientas/deskops python -m pytest -q tests/test_vitest_suite.py
3) Citen ese archivo en references de la tarea (junto al sha del commit); deskops closeout verify lo cuenta como evidencia de tests.

Referencia: docs/workflow-policy-reference.md de deskops, sección "Tests evidence from a suite in another language".
