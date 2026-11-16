---
sldb:
  by: agent
  at: '2026-11-16T05:44:26Z'
  authority: generated
  via: save_document_payload
# board-xxx
id: board-001
# Affected workspace or domain
scope: desk
# List of task-xxx paths
tasks:
- desk/tasks/task-fase-0-ir-scion-build-pasa-el-contexto-por-stdin-el-docker-snap-no-lee-scion.md
- desk/tasks/task-fase-0-ir-hook-pre-start-deskops-tools-instala-sldb-y-deskops-editables-desde-workspace.md
- desk/tasks/task-fase-0-ir-template-del-ejecutor-de-ir-con-tmp-en-ram-lock-de-tests-compartido-y-tope-de-memoria.md
- desk/tasks/task-endpoint-no-loopback-del-hub-de-scion-de-producción-para-ejecutores-pi-en-red-bridge-decisión-de-jp.md
- desk/tasks/task-hook-deskops-tools-venv-de-test-del-repo-de-la-tarea-pytest-pytest-xdist-y-extras-de-test-dentro-del.md
- desk/tasks/task-hub-de-scion-listener-de-solo-hub-api-para-agentes-en-la-ip-del-bridge-sin-web-ni-dev-auth.md
- desk/tasks/task-regla-ufw-que-abre-en-docker0-solo-el-listener-de-agentes-del-hub-de-scion-acción-de-jp-con-sudo.md
- desk/tasks/task-ejecutores-pi-en-red-bridge-contra-el-listener-de-agentes-del-hub.md
# List of pill-xxx paths
pills:
- desk/contexts/pills.md
# List of ritual-xxx paths
rituals:
- desk/rituals/phase.md
- desk/rituals/execution.md
- desk/rituals/testing.md
- desk/rituals/closeout.md
# e.g., system:sldb, workspace:desk
tags:
- workspace:desk
---

# scion Board

## Purpose

_Explain what this board routes and why it exists._

Route the active execution set for scion.

## Notes

_Add short operational notes about the current routed set._

Bootstrap complete. Add active task docs under `desk/tasks/` and route them here.

## Task Details

_Generated from the task references above._

- Fase 0 IR: scion build pasa el contexto por stdin (el docker snap no lee ~/.scion) [draft] - `scion build <harness-config>` construye con docker aunque el CLI de docker no pueda leer ~/.scion: scion empaqueta el directorio del harness-config como tar y lo pasa por stdin (`docker build ... -`). podman y Apple container conservan el directorio como argumento. `--dry-run` muestra el comando equivalente (`tar -C <dir> -cf - . | docker build ... -`).
- Fase 0 IR: hook pre-start deskops-tools instala sldb y deskops editables desde /workspace [draft] - hooks/pre-start-deskops.sh instala sldb y deskops con `uv tool install --editable` directamente desde $SCION_WORKSPACE/sldb y $SCION_WORKSPACE/deskops (por defecto /workspace), con sldb también editable dentro del venv de deskops (`--with-editable`). Un cambio en /workspace/sldb o /workspace/deskops se ve en el siguiente comando del agente sin reinstalar.
- Fase 0 IR: template del ejecutor de IR con tmp en RAM, lock de tests compartido y tope de memoria [draft] - 1) deskops: `deskops add|edit|list|show role` y `... runtime-profile`; el --context-file de `deskops runtime template` acepta claves opcionales memory_limit, cpu_limit, shared_paths y env, que salen como resources.limits, volúmenes con la misma ruta y env en scion-agent.yaml. 2) Desk de IR: un RoleDoc del ejecutor (kind claude, con las reglas del brief dentro del rol) y un RuntimeProfileDoc claude, creados con deskops. 3) Template generado con deskops runtime template + context file (TMPDIR=/dev/shm, /dev/shm compartido, tope de memoria). 4) Medición: un test real de sldb que hace fsync, dentro del contenedor de la imagen del fork con esos montajes, dura < 2 s.
- Endpoint no loopback del hub de scion de producción para ejecutores pi en red bridge (decisión de JP) [draft] - JP decide si el hub de producción en :8080 pasa a escuchar en un endpoint no loopback alcanzable desde la red bridge de docker y con cuál de las opciones de la propuesta, o si sigue en loopback.
- Hook deskops-tools: venv de test del repo de la tarea (pytest, pytest-xdist y extras de test) dentro del contenedor [draft] - Al terminar el hook, dentro del contenedor existe un venv de test del repo de la tarea en $HOME/.venvs/task, con ese repo instalado editable con su extra de test, sldb editable con los extras mcp y code, pytest-xdist==3.8.0, y enlaces pytest y task-python en $HOME/.local/bin que apuntan a ese venv. Con eso, cd $DESKOPS_DESK_ROOT && pytest -q -n 2 <archivo> funciona sin PYTHONPATH a mano.
- Hub de scion: listener de solo Hub API para agentes en la IP del bridge, sin web ni dev-auth [draft] - scion server start acepta --agent-api-host <ip> y --agent-api-port <puerto>, que van juntos (uno solo es error de arranque con un mensaje que nombre ambos flags). Con ambos, el hub abre un http.Server extra en <ip>:<puerto> con el mismo handler de Hub API, detrás de un guard de solo agentes: /healthz, /health y /readyz responden sin auth; cualquier otro path exige un token de agente válido (lo que reconoce extractAgentToken en pkg/hub/auth.go: header X-Scion-Agent-Token o JWT de agente en Bearer) y, si no lo trae, da 401, incluso /api/v1/auth/* y los tokens scion_dev_*, scion_pat_* o de sesión web. Lo que un agente puede hacer sigue limitado por los scopes de su token (authz, sin cambios). No se sirve la web. computeContainerHubEndpoint usa el orden: runtime_broker.container_hub_endpoint configurado > listener de agentes > dominio público o IAP (lo de hoy) > host.docker.internal (lo de hoy). Sin los flags, el comportamiento es idéntico al actual.
- Regla ufw que abre en docker0 solo el listener de agentes del hub de scion (acción de JP con sudo) [draft] - JP aplica (o rechaza) la regla que abre en docker0 solo los puertos del listener de agentes: 18090 para el hub de lab y 8090 para el de producción.
- Ejecutores pi en red bridge contra el listener de agentes del hub [draft] - Un agente pi lanzado por scion contra un hub de lab con --agent-api-host 172.17.0.1 --agent-api-port 18090 corre con NetworkMode distinto de host, alcanza el listener de agentes desde dentro del contenedor y no alcanza 127.0.0.1:15432, 172.17.0.1:15432 ni 172.17.0.1:8000. Con eso queda probada, en el lab, la configuración que JP aplicará en producción (puerto 8090).
