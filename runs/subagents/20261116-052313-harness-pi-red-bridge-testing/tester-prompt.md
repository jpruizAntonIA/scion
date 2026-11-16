Eres el TESTER independiente deskops-t-e2f0d5d6a151 (rol deskops-tester, intento 1) del desk de scion. Corres en herdr en robocop2, no en Scion: ignora sciontool; al terminar di "LISTO" en tu última línea.

Tarea: task-harness-pi-en-desk-real-red-bridge-para-ejecutores-imagen-con-pytest-dagster-spec2viz-sldb-en-el-wor
Raíz: /mnt/ssd/proyectos/SLDB_1/scion. Tu run_dir (no inventes otro): runs/subagents/20261116-052313-harness-pi-red-bridge-testing

1. Lee tu rol: runs/subagents/20261116-052313-harness-pi-red-bridge-testing/scion-template/agents.md (/workspace/<repo> = /mnt/ssd/proyectos/SLDB_1/scion).
2. Lee el contrato: deskops show task task-harness-pi-en-desk-real-red-bridge-para-ejecutores-imagen-con-pytest-dagster-spec2viz-sldb-en-el-wor --root /mnt/ssd/proyectos/SLDB_1/scion. El coordinador lo acotó tras la ejecución: lanzar agentes en bridge pasó a otra tarea. Prueba el contrato tal como está ahora.
3. Lo que pruebas: el diff sin commitear de harnesses/pi/ y los artefactos del ejecutor en runs/subagents/20261116-052313-harness-pi-red-bridge (mepu-sldb.txt, probe-red.txt, propuesta-endpoint-hub.md). Corre TÚ las validaciones que se pueden correr (docker run de la imagen, provision_test, cmp, git diff --stat, greps, limpieza), una a la vez, con TMPDIR=/dev/shm. Guarda comando y exit code en runs/subagents/20261116-052313-harness-pi-red-bridge-testing/validation.log.
4. Revisa también: que la imagen scion-pi:f6e623c69 corresponde al Dockerfile del diff (la build no tiene que repetirse: compara las capas o el resultado del smoke); que la propuesta cita archivos y líneas que existen en cmd/ y pkg/ (abre 2 o 3 de las citas); y que el diff no toca nada fuera de harnesses/pi/Dockerfile y README.md.
5. Escribe runs/subagents/20261116-052313-harness-pi-red-bridge-testing/result-summary.md con PASS o FAIL por validación y uno global, y los hallazgos.

Prohibido: modificar archivos fuera de tu run_dir, arreglar, commitear, cerrar, editar desk/ o .sldb/, git add -A, --autostash, pkill, pgrep, worktrees, scion server, tocar ~/.scion o el hub de :8080, dejar archivos en /dev/shm, suites completas.
