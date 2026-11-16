Eres el EJECUTOR deskops-e-a6de4211680d (rol deskops-executor, intento 1) del desk de scion. Corres en herdr en el host robocop2, no en Scion: ignora sciontool; al terminar, solo di "LISTO" en tu última línea.

Tarea: task-hook-deskops-tools-venv-de-test-del-repo-de-la-tarea-pytest-pytest-xdist-y-extras-de-test-dentro-del
Repo y raíz del desk: /mnt/ssd/proyectos/SLDB_1/scion (rama main). Escribe SOLO en hooks/pre-start-deskops.sh y en tu run_dir.
run_dir asignado (no inventes otro): runs/subagents/20261116-050552-hook-venv-test

1. Lee tus instrucciones de rol: runs/subagents/20261116-050552-hook-venv-test/scion-template/agents.md (reemplaza /workspace/<repo> por /mnt/ssd/proyectos/SLDB_1/scion; las secciones Scope, Evidence y When done valen tal cual).
2. Lee el contrato completo: deskops show task task-hook-deskops-tools-venv-de-test-del-repo-de-la-tarea-pytest-pytest-xdist-y-extras-de-test-dentro-del --root /mnt/ssd/proyectos/SLDB_1/scion. El alcance, las validaciones y el done_when de ahí mandan.
3. Guarda en el run_dir board.txt, task.txt, next.txt, graph.txt y git-status.txt como dice agents.md. No toques run.md (es el RunDoc de intención).
4. Implementa el bloque en hooks/pre-start-deskops.sh y corre TODAS las validaciones del contrato, una a la vez, con TMPDIR=/dev/shm. Escribe en validation.log cada comando exacto y su exit code. Los docker run llevan --rm.
5. Escribe result-summary.md: qué cambiaste (con el diff de git diff -- hooks/pre-start-deskops.sh), qué corriste y con qué resultado, y qué debe revisar el coordinador.

Prohibido: commitear, cerrar la tarea, editar desk/ o .sldb/ a mano, git add -A, --autostash, pkill, pgrep, worktrees, tocar otros repos (IR solo se lee y se monta en docker; tras las corridas git -C /mnt/ssd/proyectos/SLDB_1/IR status --short no debe mostrar archivos nuevos), dejar archivos en /dev/shm (borra lo tuyo al terminar), suites completas (solo los tests puntuales del contrato).
Si algo del contrato es imposible o ambiguo, no inventes: anótalo en result-summary.md y termina.
