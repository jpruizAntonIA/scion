---
sldb:
  by: agent
  at: '2026-11-26T02:36:52Z'
  authority: generated
  via: create_document
id: task-decision-de-jp-que-canales-de-discord-se-enlazan-y-si-extras-scion-discord-va-al-hub-de-produccion-d
status: draft
summary: ''
tags: []
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
closeout_evidence:
- commit
- document
---

# Decisión de JP: qué canales de Discord se enlazan y si extras/scion-discord va al hub de producción de robocop2

## Rationale

_Explain why this task exists or the business driver behind it._

Nota de Governance 20261120-212728: personas y agentes se hablan por canales distintos; extras/scion-discord es un broker en los dos sentidos con nombre y avatar por agente. Necesita el fork al día. Anotado en sala/2026-11-25-planificacion/scion.md punto 5.

## Goal

_Describe the concrete result this task must produce._

JP decide si el plugin se instala, en qué hub (lab o producción de robocop2) y qué canales del equipo se enlazan.

## Scope

_State what is in scope and what is out of scope._

IN: la lista de canales, el hub y la decisión de instalar o no. OUT: instalar el plugin y sus credenciales (otra tarea, dependiente del fork al día).

## Implementation Path

_Outline the expected implementation route or affected surface._



## Validation

_List the checks required before this task can close._

- deskops review status de esta tarea muestra el recibo owner dispuesto por JP con los canales y el hub, o con el rechazo y su razón

## Done When

_Name the observable condition that makes the task complete._

JP dispuso el recibo owner con los canales, el hub y la razón, o con el rechazo.
