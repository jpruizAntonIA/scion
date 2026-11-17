---
sldb:
  by: agent
  at: '2026-11-17T01:22:57Z'
  authority: generated
  via: save_document_payload
id: task-los-agentes-scion-toman-el-lock-de-tests-compartido-con-el-uid-del-host-protected-regular-2
status: draft
summary: ''
tags:
- workspace:desk
- artifact:task
current_node: ritual-execution
history: []
references: []
depends_on: []
pills: []
files: []
task_type: task.code
inherits_from: []
inherit_acceptance_context: false
atoms: []
from_drawer: desk/drawer/tasks/task-los-agentes-scion-toman-el-lock-de-tests-compartido-con-el-uid-del-host-protected-regular-2.md
---

# Los agentes scion toman el lock de tests compartido con el uid del host (protected_regular=2)

## Rationale

_Explain why this task exists or the business driver behind it._

En robocop2 fs.protected_regular=2 y /dev/shm/sldb1-tests.lock es de robocop (1001). Un contenedor de ghcr.io/jpruizantonia/scion-claude:f6e623c69 que corre como root (sin SCION_HOST_UID/GID) recibe EACCES al abrir el lock con O_CREAT: flock -n da rc 66 y la suite del agente falla o corre sin lock. Si el lock no existiera y lo creara un contenedor root, el host ya no podría abrirlo. Hallado por el tester deskops-t-8bfe438ea7fe (runs/subagents/20261116-180814-template-ir-testing); con --user 1001:1001 o SCION_HOST_UID=1001/SCION_HOST_GID=1001 el lock funciona (runs/subagents/20261116-180814-template-ir-lock-testing).

## Goal

_Describe the concrete result this task must produce._

Un agente lanzado por scion con el template ir-executor de IR corre con el uid del host (sciontool realinea el usuario scion a SCION_HOST_UID/GID) y toma /dev/shm/sldb1-tests.lock: rc 1 si el host lo sostiene, rc 0 si está libre. El lock lo crea siempre el host, nunca un contenedor.

## Scope

_State what is in scope and what is out of scope._

IN: verificar si el runtime de scion (broker del fork, commit f6e623c69 o posterior) pasa SCION_HOST_UID/GID a los contenedores de agentes locales (cmd/root.go y cmd/sciontool/commands/init.go, setupHostUser); si no lo pasa, fijarlo en el template de IR (env de IR/.scion/templates/ir-executor vía deskops runtime template --context-file /mnt/ssd/proyectos/SLDB_1/.bootstrap/ir-scion-context.json, nunca editando el template generado a mano) o en el código del runtime; documentar en el rol ir-executor que el lock lo crea el host. OUT: cambiar fs.protected_regular de la máquina, cambiar el dueño o el modo del lock, la suite de IR.

## Implementation Path

_Outline the expected implementation route or affected surface._

1) Leer en cmd/ cómo el runtime local arma el env del contenedor y si incluye SCION_HOST_UID/GID. 2) Si lo incluye: solo verificación con un agente sonda (requiere OK de JP para arrancar un agente). 3) Si no: agregar SCION_HOST_UID/GID al env del context file y regenerar el template con deskops runtime template, o corregir el runtime con su test Go y un tests/test_*.py que lo corra con deskops.testing.

## Validation

_List the checks required before this task can close._

- Desde el contenedor de un agente lanzado con scion start y el template ir-executor (con OK de JP para arrancarlo): id -u imprime 1001; con el host sosteniendo flock /dev/shm/sldb1-tests.lock, flock -n /dev/shm/sldb1-tests.lock true da rc 1; con el lock libre da rc 0
- ls -l /dev/shm/sldb1-tests.lock muestra dueño robocop después de las pruebas
- Si se tocó código Go: el test .py nuevo bajo tests/ que corre ese test Go con deskops.testing pasa con TMPDIR=/dev/shm uv run --no-project --with pytest --with-editable /mnt/ssd/herramientas/deskops python -m pytest -q, y su ruta queda en references de la tarea

## Done When

_Name the observable condition that makes the task complete._

Un agente scion real con el template ir-executor toma y respeta el lock de tests compartido como uid 1001, con la evidencia en el run_dir.
