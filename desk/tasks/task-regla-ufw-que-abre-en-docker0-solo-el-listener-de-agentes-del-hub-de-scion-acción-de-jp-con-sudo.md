---
sldb:
  by: agent
  at: '2026-11-16T05:40:42Z'
  authority: generated
  via: save_document_payload
id: task-regla-ufw-que-abre-en-docker0-solo-el-listener-de-agentes-del-hub-de-scion-acción-de-jp-con-sudo
status: draft
summary: ''
tags:
- workspace:desk
- artifact:task
- host:robocop2
current_node: ritual-execution
history: []
references: []
depends_on: []
pills: []
files: []
task_type: task.decision
inherits_from: []
inherit_acceptance_context: false
atoms: []
---

# Regla ufw que abre en docker0 solo el listener de agentes del hub de scion (acción de JP con sudo)

## Rationale

_Explain why this task exists or the business driver behind it._

ufw está activo con DEFAULT_INPUT_POLICY=DROP (/etc/default/ufw): desde un contenedor en red bridge, 172.17.0.1:8000 y :15432 hacen timeout aunque escuchan en 0.0.0.0, que es el aislamiento buscado. Por la misma razón, el listener de agentes del hub en 172.17.0.1 no es alcanzable desde el bridge sin una regla allow. Abrirla requiere sudo, y por eso es de JP. Evidencia: runs/subagents/20261116-052313-harness-pi-red-bridge/propuesta-endpoint-hub.md y runs/subagents/20261116-052313-harness-pi-red-bridge/probe-red.txt.

## Goal

_Describe the concrete result this task must produce._

JP aplica (o rechaza) la regla que abre en docker0 solo los puertos del listener de agentes: 18090 para el hub de lab y 8090 para el de producción.

## Scope

_State what is in scope and what is out of scope._

IN: una regla y su confirmación: sudo ufw allow in on docker0 to 172.17.0.1 port 8090,18090 proto tcp comment 'scion: listener de agentes del hub'; vuelta atrás: sudo ufw delete allow in on docker0 to 172.17.0.1 port 8090,18090 proto tcp. Antes, JP confirma con sudo ufw status verbose que no haya ya un allow amplio sobre docker0. OUT: abrir 8080 (web y dev-auth siguen en loopback), los servicios del host 8000 y 15432 (siguen en DROP) y cualquier otra regla.

## Implementation Path

_Outline the expected implementation route or affected surface._

JP corre con ! en su terminal: sudo ufw status verbose; sudo ufw allow in on docker0 to 172.17.0.1 port 8090,18090 proto tcp comment 'scion: listener de agentes del hub'; sudo ufw status numbered. Luego dispone el recibo owner de esta tarea con la salida o la razón del rechazo.

## Validation

_List the checks required before this task can close._

- deskops review status de esta tarea muestra el recibo owner dispuesto por JP con la salida de sudo ufw status numbered que incluye la regla, o con el rechazo y su razón

## Done When

_Name the observable condition that makes the task complete._

JP dispuso el recibo owner: aplicada (con la línea de ufw status que la muestra) o rechazada (con la razón).
