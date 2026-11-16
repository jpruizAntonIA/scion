---
sldb:
  by: agent
  at: '2026-11-16T03:41:00Z'
  authority: generated
  via: create_document
id: task-endpoint-no-loopback-del-hub-de-scion-de-producción-para-ejecutores-pi-en-red-bridge-decisión-de-jp
status: draft
summary: ''
tags:
- workspace:desk
- artifact:task
current_node: ritual-execution
history: []
references: []
depends_on:
- task-harness-pi-en-desk-real-red-bridge-para-ejecutores-imagen-con-pytest-dagster-spec2viz-sldb-en-el-wor
pills: []
files: []
task_type: task.decision
inherits_from: []
inherit_acceptance_context: false
atoms: []
---

# Endpoint no loopback del hub de scion de producción para ejecutores pi en red bridge (decisión de JP)

## Rationale

_Explain why this task exists or the business driver behind it._

Hoy el hub de scion de producción (robocop2, puerto 8080) escucha en loopback, así que los ejecutores pi corren con --network=host; en el piloto de mepu (2026-11-11, heyantonia/mepu#246) un ejecutor llegó a mepu_test con datos reales. Pasar a red bridge exige que el hub sea alcanzable desde la red de docker, y cambiar cómo escucha el hub de producción (bind, firewall, quién más lo alcanza) es una decisión de JP.

## Goal

_Describe the concrete result this task must produce._

JP decide si el hub de producción en :8080 pasa a escuchar en un endpoint no loopback alcanzable desde la red bridge de docker y con cuál de las opciones de la propuesta, o si sigue en loopback.

## Scope

_State what is in scope and what is out of scope._

IN: una decisión con su respuesta: (a) aplicar la propuesta de endpoint (y cuál variante: IP del bridge docker 172.17.0.1, host.docker.internal con bind explícito, u otra que proponga la tarea de código), (b) dejar el hub en loopback y mantener --network=host, o (c) otra condición que JP indique. OUT: aplicar el cambio (reiniciar el hub es una acción de JP con ! en su terminal), el trabajo de lab y la imagen pi, que hace la tarea de código de la que depende.

## Implementation Path

_Outline the expected implementation route or affected surface._

JP lee runs/<run-dir>/propuesta-endpoint-hub.md que deja la tarea task-harness-pi-en-desk-real-red-bridge-para-ejecutores-imagen-con-pytest-dagster-spec2viz-sldb-en-el-wor (opciones, riesgos, el probe del lab y los comandos exactos de aplicación y vuelta atrás) y dispone el recibo owner de esta tarea con su elección.

## Validation

_List the checks required before this task can close._

- deskops review status de esta tarea muestra el recibo owner dispuesto por JP con una razón que nombra (a), (b) o (c)

## Done When

_Name the observable condition that makes the task complete._

JP dispuso el recibo owner de esta tarea con una razón que elige (a) con su variante, (b) o (c); una respuesta sin elección no cierra.
