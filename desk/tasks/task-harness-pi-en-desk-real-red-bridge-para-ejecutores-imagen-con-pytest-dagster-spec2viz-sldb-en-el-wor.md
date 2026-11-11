---
sldb:
  by: agent
  at: '2026-11-11T04:07:03Z'
  authority: generated
  via: create_document
id: task-harness-pi-en-desk-real-red-bridge-para-ejecutores-imagen-con-pytest-dagster-spec2viz-sldb-en-el-wor
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
files:
- harnesses/pi/Dockerfile
- harnesses/pi/README.md
- harnesses/pi/provision.py
- harnesses/pi/provision_test.py
task_type: task.code
inherits_from: []
inherit_acceptance_context: false
atoms: []
from_drawer: desk/drawer/tasks/task-harness-pi-en-desk-real-red-bridge-para-ejecutores-imagen-con-pytest-dagster-spec2viz-sldb-en-el-worktree.md
---

# Harness pi en desk real: red bridge para ejecutores, imagen con pytest/dagster/spec2viz, .sldb en el worktree

## Rationale

_Explain why this task exists or the business driver behind it._

Primer piloto del harness pi en un desk real (mepu, 2026-11-11: DOC-12, 2 commits, 92 tests verdes; heyantonia/mepu#246). Con el Hub en loopback los ejecutores corren con --network=host y uno llegó a mepu_test con datos reales. La imagen no trae las herramientas del desk y el worktree de tarea no trae .sldb.

## Goal

_Describe the concrete result this task must produce._

Los ejecutores pi corren en red bridge sin alcanzar servicios del host, con la imagen ya equipada para los desks de SLDB_1 y con el store .sldb disponible en su worktree de tarea.

## Scope

_State what is in scope and what is out of scope._

IN, por prioridad: (1) PRIORIDAD: red bridge para ejecutores pi (sin --network=host ni SCION_FORCE_HOST_NETWORK), probada DESDE DENTRO del contenedor: 127.0.0.1:15432 (Postgres local) no responde y tampoco lo hacen los servicios del host en 0.0.0.0, incluido descarga-adjuntos en :8000 vía la IP del gateway. Requiere un endpoint del Hub que no sea loopback: el cambio de endpoint se COORDINA CON JP y no se aplica sin su decisión; hasta entonces se prepara y se prueba en ~/lab-scion. (2) pytest, dagster y spec2viz instalados en la imagen pi (hoy el ejecutor arma un venv en /tmp). (3) El worktree de tarea trae .sldb (en mepu está gitignored), de modo que `make codigo-doc` corre dentro del contenedor. OUT: push (origin da 403), credenciales, cambios en otros harnesses, datos reales de mepu.

## Implementation Path

_Outline the expected implementation route or affected surface._

Partir del bundle harnesses/pi de la rama local wt/pi-harness (7163525f9) y de la imagen fork scion-pi-fork usada en el piloto. (1) Inventariar cómo scion elige la red (SCION_FORCE_HOST_NETWORK, endpoint del Hub) y proponer a JP el endpoint no loopback (p. ej. la IP del bridge docker o host.docker.internal con un bind explícito); con el endpoint de lab, lanzar un ejecutor en bridge y guardar como evidencia un probe desde dentro del contenedor (python/bash /dev/tcp) contra 127.0.0.1:15432, gateway:15432 y gateway:8000 que debe fallar, y contra el Hub, que debe responder. (2) Agregar pytest, dagster y spec2viz a harnesses/pi/Dockerfile con versiones fijadas y comprobar import y --version dentro de la imagen. (3) Hacer que el aprovisionamiento del worktree de tarea copie o monte el .sldb del desk (sin secretos), y verificar `make codigo-doc` dentro del contenedor.

## Validation

_List the checks required before this task can close._

- Probe de red desde dentro de un contenedor pi en bridge: 127.0.0.1:15432, <gateway>:15432 y <gateway>:8000 rechazados o con timeout; el Hub alcanzable (salida guardada en runs/)
- docker inspect del contenedor del ejecutor: NetworkMode distinto de host
- docker run scion-pi: python3 -c 'import pytest, dagster' y spec2viz --version terminan en exit 0
- En el worktree de tarea dentro del contenedor: .sldb presente y make codigo-doc termina en exit 0 (mepu de prueba, sin datos reales)
- TMPDIR=/dev/shm timeout 900 systemd-run --user --scope -q -p MemoryMax=2G -- python3 harnesses/pi/provision_test.py pasa

## Done When

_Name the observable condition that makes the task complete._

Las tres mejoras están commiteadas en local con evidencia en runs/. El aislamiento de red está probado desde dentro del contenedor contra un Hub no loopback. El cambio del endpoint del Hub en producción queda aplicado solo si JP lo aprobó; si no, queda registrado como bloqueo pendiente de JP con la propuesta concreta.
