# result-summary — run-deskops-e-c84637e8b566 (executor, intento 1)

Tarea: task-fase-0-ir-template-del-ejecutor-de-ir-con-tmp-en-ram-lock-de-tests-compartido-y-tope-de-memoria

## Qué hice
- Creé `tests/test_deskops_ir_template_suite.py` (único archivo nuevo en tests/; sin commitear), puente con
  `deskops.testing.foreign_suites.run_foreign_suite` que declara la evidencia de Validation puntos 1 y 2.
- Checkout de deskops: `DESKOPS_TEST_CHECKOUT` o `/mnt/ssd/herramientas/deskops`; sldb: `SLDB_TEST_CHECKOUT` o
  `/mnt/ssd/herramientas/sldb`. env = os.environ con TMPDIR=/dev/shm por defecto.
- Fixture autouse (scope module): `git merge-base --is-ancestor <c> HEAD` para 4a7707a5, 4c745c18, 881e177a
  (vía run_foreign_suite; falla si alguno no es ancestro).
- Un test por archivo del contrato, con `uv run --no-project --with pytest --with-editable <deskops>
  --with-editable <sldb> python -m pytest -q -p no:cacheprovider <archivo>`, cwd=<deskops>:
  test_scion_runtime.py, test_role_runtime_artifacts.py, test_command_registry.py (timeout 600) y
  test_output_goldens.py -k test_help_goldens (timeout 1200).

## Validación
- Comando y exit code en `validation.log`; salida en `pytest-output.txt`.
- Resultado: `4 passed in 795.80s` — exit 0. Checkout de deskops en 339bacca (HEAD de /mnt/ssd/herramientas/deskops).

## Veredicto
PASS. Para el closeout: `--test tests/test_deskops_ir_template_suite.py`.

## Notas para el supervisor
- Validation puntos 3 y 4 (medición fsync en docker y lock flock) no los cubre este test; quedan con la evidencia
  previa de los testers.
- Los checkouts de deskops y sldb quedaron limpios (git status vacío).
- Los tests de deskops dejaron `/dev/shm/tmpeoew9cit` (raíz temporal con .sldb, creada a las 22:32 durante la corrida, sin
  uso abierto); la borré. Quedan locks vacíos uv-*.lock de uv en /dev/shm (son de uv y compartidos, no los toqué).
- La corrida tarda ~13 min (goldens domina).
