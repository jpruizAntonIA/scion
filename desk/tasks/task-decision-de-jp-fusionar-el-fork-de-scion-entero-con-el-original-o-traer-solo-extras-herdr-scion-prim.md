---
sldb:
  by: agent
  at: '2026-11-26T02:36:50Z'
  authority: generated
  via: create_document
id: task-decision-de-jp-fusionar-el-fork-de-scion-entero-con-el-original-o-traer-solo-extras-herdr-scion-prim
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

# Decisión de JP: fusionar el fork de scion entero con el original o traer solo extras/herdr-scion primero

## Rationale

_Explain why this task exists or the business driver behind it._

El fork está 795 commits atrás de GoogleCloudPlatform/scion y 47 adelante; extras/herdr-scion solo existe en el original (nota de Governance 20261120-212719). Decisión de JP pendiente, anotada en sala/2026-11-25-planificacion/scion.md punto 5.

## Goal

_Describe the concrete result this task must produce._

JP elige: (A) fusionar el original entero en una rama aparte, con binario e imágenes del mismo commit y otro tag, ensayado contra el piloto de IR; o (B) copiar solo extras/herdr-scion como paso 0 y reconciliar después. También decide herdr 0.9.1 (lo que pide el tablero) frente a 0.9.0 (laptop de JP).

## Scope

_State what is in scope and what is out of scope._

IN: la elección A o B, la versión de herdr y su razón. OUT: ejecutar la fusión (otra tarea task.code, que depende de esta y no se crea aquí).

## Implementation Path

_Outline the expected implementation route or affected surface._



## Validation

_List the checks required before this task can close._

- deskops review status de esta tarea muestra el recibo owner dispuesto por JP con la elección y su razón

## Done When

_Name the observable condition that makes the task complete._

JP dispuso el recibo owner con A o B, la versión de herdr y la razón.
