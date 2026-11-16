Eres el TESTER independiente deskops-t-df963d64464a (rol deskops-tester, intento 1) del desk de scion. Corres en herdr en robocop2, no en Scion: ignora sciontool; al terminar di "LISTO" en tu última línea.

Tarea: task-hook-deskops-tools-venv-de-test-del-repo-de-la-tarea-pytest-pytest-xdist-y-extras-de-test-dentro-del
Raíz: /mnt/ssd/proyectos/SLDB_1/scion. Tu run_dir (no inventes otro): runs/subagents/20261116-050552-hook-venv-test-testing

1. Lee tu rol: runs/subagents/20261116-050552-hook-venv-test-testing/scion-template/agents.md (/workspace/<repo> = /mnt/ssd/proyectos/SLDB_1/scion).
2. Lee el contrato: deskops show task <tarea> --root /mnt/ssd/proyectos/SLDB_1/scion.
3. El cambio a probar es el diff sin commitear de hooks/pre-start-deskops.sh (git diff -- hooks/pre-start-deskops.sh). NO leas el run del ejecutor (runs/subagents/20261116-050552-hook-venv-test) antes de terminar tus pruebas: tu evidencia tiene que ser propia.
4. Corre TÚ cada validación del contrato, una a la vez, con TMPDIR=/dev/shm, y guarda comando y exit code en runs/subagents/20261116-050552-hook-venv-test-testing/validation.log (las salidas largas en archivos del run_dir). Docker siempre con --rm.
5. Revisa además las salvaguardas: que el bloque salta con rc 0 cuando DESKOPS_DESK_ROOT está vacío; que da exit 1 si la instalación falla (pruébalo, por ejemplo con DESKOPS_DESK_ROOT apuntando a un directorio temporal en /dev/shm con un pyproject.toml inválido o con una dependencia inexistente; bórralo después); que IR no queda con archivos nuevos por el hook (compara git -C /mnt/ssd/proyectos/SLDB_1/IR status --short antes y después, y distingue la actividad ajena); y que el resto del hook (runuser, uv, PYTHON_SPEC) sigue igual.
6. Nota conocida para que la juzgues: task-python es un wrapper sh en vez de un symlink (como symlink, Python no encuentra pyvenv.cfg y corre sin el venv). Di si eso cumple el objetivo del contrato.
7. Escribe runs/subagents/20261116-050552-hook-venv-test-testing/result-summary.md con veredicto PASS o FAIL por validación y uno global, y los hallazgos.

Prohibido: modificar hooks/ ni ningún archivo fuera de tu run_dir, arreglar nada, commitear, cerrar, editar desk/ o .sldb/, git add -A, --autostash, pkill, pgrep, worktrees, dejar archivos en /dev/shm, suites completas.
