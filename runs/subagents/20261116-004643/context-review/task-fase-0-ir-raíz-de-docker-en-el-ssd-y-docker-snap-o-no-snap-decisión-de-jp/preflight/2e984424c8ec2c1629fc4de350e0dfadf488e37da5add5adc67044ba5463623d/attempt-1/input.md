FILE:desk/tasks/task-fase-0-ir-raíz-de-docker-en-el-ssd-y-docker-snap-o-no-snap-decisión-de-jp.md
---
sldb:
  by: agent
  at: '2026-11-16T00:45:40Z'
  authority: generated
  via: create_document
id: task-fase-0-ir-raíz-de-docker-en-el-ssd-y-docker-snap-o-no-snap-decisión-de-jp
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
task_type: task.decision
inherits_from: []
inherit_acceptance_context: false
atoms: []
---

# Fase 0 IR: raíz de docker en el SSD y docker snap o no-snap (decisión de JP)

## Rationale

_Explain why this task exists or the business driver behind it._

La raíz de docker está en /var/snap/docker/common/var-lib-docker, en el HDD rotacional que es el cuello de botella de IO de robocop2; cada imagen de harness pesa 3-4 GB y la capa escribible de cada agente también vive ahí. El docker snap además no lee directorios ocultos de $HOME. Mover la raíz o cambiar de docker es decisión de JP (brief scion-piloto-ir, fase 0 punto 2).

## Goal

_Describe the concrete result this task must produce._

JP decide si mueve la raíz de docker al SSD (/mnt/ssd/docker) y si cambia el docker snap por docker-ce de apt, con la recomendación y los comandos exactos del informe reports/scion-piloto-ir-20261115.md.

## Scope

_State what is in scope and what is out of scope._

IN: la decisión y su registro. OUT: ejecutar el cambio sin JP.

## Implementation Path

_Outline the expected implementation route or affected surface._



## Validation

_List the checks required before this task can close._

- deskops review status de esta tarea muestra la disposición de JP

## Done When

_Name the observable condition that makes the task complete._

JP dispone la decisión.

FILE:instruccion
Preflight solo-TaskDoc de la tarea task-fase-0-ir-raíz-de-docker-en-el-ssd-y-docker-snap-o-no-snap-decisión-de-jp: reformula el encargo tal como lo leería un ejecutor sin ningún otro contexto, lista ambigüedades con cita textual del input y da el DRY-RUN sin ejecutar nada. No ejecutes nada.

