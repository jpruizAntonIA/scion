---
id: task-harness-pi-en-desk-real-red-bridge-para-ejecutores-imagen-con-pytest-dagster-spec2viz-sldb-en-el-worktree
status: deferred
summary: ''
tags:
- workspace:desk
- artifact:task
- source:inbox
current_node: ''
history: []
references: []
depends_on: []
pills: []
files: []
task_type: ''
inherits_from: []
inherit_acceptance_context: false
atoms: []
---

# Harness pi en desk real: red bridge para ejecutores, imagen con pytest/dagster/spec2viz, .sldb en el worktree

## Rationale

_Explain why this task exists or the business driver behind it._

Promoted from the inbox note `desk/inbox/20261111-010459-suggestion-harness-pi-en-un-desk-real-piloto-mepu-11-11-1-aislamiento-de-red.md`.

## Goal

_Describe the concrete result this task must produce._

Triage and resolve the inbox message promoted from `desk/inbox/20261111-010459-suggestion-harness-pi-en-un-desk-real-piloto-mepu-11-11-1-aislamiento-de-red.md`.

## Scope

_State what is in scope and what is out of scope._

_Describe the incoming message with enough evidence to triage._

Harness pi en un desk real (piloto mepu, 11-11): (1) aislamiento de red: con el Hub en loopback los ejecutores van con --network=host y alcanzan los Postgres locales con datos reales; hace falta un endpoint del Hub no loopback (sin SCION_FORCE_HOST_NETWORK) y un test desde dentro del contenedor que muestre que 127.0.0.1:15432 no responde (ojo: descarga-adjuntos escucha en 0.0.0.0:8000); (2) la imagen scion-pi-fork no trae pytest, dagster ni spec2viz, y el ejecutor armó un venv en /tmp; (3) el worktree de tarea no trae .sldb (store gitignored en mepu) y make codigo-doc no corre dentro. Detalle en ~/.claude memoria de mepu y en heyantonia/mepu#246.

## Implementation Path

_Outline the expected implementation route or affected surface._

To be defined when the task is promoted.

## Validation

_List the checks required before this task can close._

- 

## Done When

_Name the observable condition that makes the task complete._

The message is resolved, answered, or promoted into active work.
