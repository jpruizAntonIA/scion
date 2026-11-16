---
# unclear | suggestion
kind: suggestion
# e.g., other_repo
sender_project: scion
# e.g., target_repo
target_project: scion
# ISO 8601 timestamp
created_at: '2026-11-16T15:37:43'
# open | closed
status: open
# project identity that acknowledged the note
# ISO 8601 timestamp, set when acknowledged
---

# Lock de tests compartido: un contenedor que corre como root no puede abrir /dev/shm/sldb1-tests.lock (protected_regular=2)

_Describe the incoming message with enough evidence to triage._

Hallado por el tester deskops-t-8bfe438ea7fe (run runs/subagents/20261116-180814-template-ir-testing) en la tarea del template del ejecutor de IR. En robocop2 fs.protected_regular=2 y el lock es de robocop (1001). Dentro de ghcr.io/jpruizantonia/scion-claude:f6e623c69 corriendo como root (docker run a secas, sciontool en modo local sin SCION_HOST_UID), flock -n /dev/shm/sldb1-tests.lock da rc 66 (EACCES) en vez de 1; con --user 1001:1001 o -e SCION_HOST_UID=1001 -e SCION_HOST_GID=1001 da rc 1, como se espera. Riesgos: (1) un agente que arranque sin SCION_HOST_UID no puede tomar el lock y su suite falla o corre sin él; (2) si el lock no existiera y lo creara un contenedor como root, el host ya no podría abrirlo. Propuesta: que el template de IR (context file .bootstrap/ir-scion-context.json, env) o el broker garanticen SCION_HOST_UID/GID, y que la fase 1 lo verifique al lanzar el primer agente. La validación del contrato se reescribió para usar el uid del host.
