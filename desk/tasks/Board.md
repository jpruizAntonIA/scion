---
sldb:
  by: agent
  at: '2026-11-26T02:36:54Z'
  authority: generated
  via: save_document_payload
# board-xxx
id: board-001
# Affected workspace or domain
scope: desk
# List of task-xxx paths
tasks:
- desk/tasks/task-regla-ufw-que-abre-en-docker0-solo-el-listener-de-agentes-del-hub-de-scion-acción-de-jp-con-sudo.md
- desk/tasks/task-ejecutores-pi-en-red-bridge-contra-el-listener-de-agentes-del-hub.md
- desk/tasks/task-los-agentes-scion-toman-el-lock-de-tests-compartido-con-el-uid-del-host-protected-regular-2.md
- desk/tasks/task-decision-de-jp-fusionar-el-fork-de-scion-entero-con-el-original-o-traer-solo-extras-herdr-scion-prim.md
- desk/tasks/task-decision-de-jp-que-canales-de-discord-se-enlazan-y-si-extras-scion-discord-va-al-hub-de-produccion-d.md
- desk/tasks/task-decision-de-jp-tope-de-agentes-del-concilio-y-de-las-pruebas-sin-contexto-en-paralelo-en-robocop2.md
# List of pill-xxx paths
pills:
- desk/contexts/pills.md
# List of ritual-xxx paths
rituals:
- desk/rituals/phase.md
- desk/rituals/execution.md
- desk/rituals/testing.md
- desk/rituals/closeout.md
# e.g., system:sldb
tags: []
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

- Regla ufw que abre en docker0 solo el listener de agentes del hub de scion (acción de JP con sudo) [draft] - JP aplica (o rechaza) la regla que abre en docker0 solo los puertos del listener de agentes: 18090 para el hub de lab y 8090 para el de producción.
- Ejecutores pi en red bridge contra el listener de agentes del hub [draft] - Un agente pi lanzado por scion contra un hub de lab con --agent-api-host 172.17.0.1 --agent-api-port 18090 corre con NetworkMode distinto de host, alcanza el listener de agentes desde dentro del contenedor y no alcanza 127.0.0.1:15432, 172.17.0.1:15432 ni 172.17.0.1:8000. Con eso queda probada, en el lab, la configuración que JP aplicará en producción (puerto 8090).
- Los agentes scion toman el lock de tests compartido con el uid del host (protected_regular=2) [draft] - Un agente lanzado por scion con el template ir-executor de IR corre con el uid del host (sciontool realinea el usuario scion a SCION_HOST_UID/GID) y toma /dev/shm/sldb1-tests.lock: rc 1 si el host lo sostiene, rc 0 si está libre. El lock lo crea siempre el host, nunca un contenedor.
- Decisión de JP: fusionar el fork de scion entero con el original o traer solo extras/herdr-scion primero [draft] - JP elige: (A) fusionar el original entero en una rama aparte, con binario e imágenes del mismo commit y otro tag, ensayado contra el piloto de IR; o (B) copiar solo extras/herdr-scion como paso 0 y reconciliar después. También decide herdr 0.9.1 (lo que pide el tablero) frente a 0.9.0 (laptop de JP).
- Decisión de JP: qué canales de Discord se enlazan y si extras/scion-discord va al hub de producción de robocop2 [draft] - JP decide si el plugin se instala, en qué hub (lab o producción de robocop2) y qué canales del equipo se enlazan.
- Decisión de JP: tope de agentes del concilio y de las pruebas sin contexto en paralelo en robocop2 [draft] - JP fija el número máximo de agentes del concilio simultáneos (propuesta: cada revisor un agente, máximo 3, más 1 lector sin memoria) y cómo cuenta contra el tope general de agentes activos.
