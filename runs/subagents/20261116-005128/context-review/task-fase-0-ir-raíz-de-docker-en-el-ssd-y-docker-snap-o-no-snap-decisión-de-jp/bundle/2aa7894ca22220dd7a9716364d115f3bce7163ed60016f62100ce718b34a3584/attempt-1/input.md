FILE:desk/tasks/task-fase-0-ir-raíz-de-docker-en-el-ssd-y-docker-snap-o-no-snap-decisión-de-jp.md
---
sldb:
  by: agent
  at: '2026-11-16T00:48:54Z'
  authority: generated
  via: save_document_payload
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

IN: dos decisiones independientes, cada una con su respuesta: (1) mover la raíz de docker del HDD (/var/snap/docker/common/var-lib-docker) al SSD (/mnt/ssd/docker, data-root en daemon.json); (2) seguir con el docker snap o pasar a docker-ce de apt. La recomendación y los comandos exactos de cada una están en la sección Fase 0 de /mnt/ssd/proyectos/SLDB_1/reports/scion-piloto-ir-20261115.md. Que el snap no lea directorios ocultos de $HOME ya no bloquea (scion build pasa el contexto por stdin, tarea hermana); pesa solo como argumento a favor de docker-ce. Registro: el worker registra JP como owner con deskops review record --kind owner; JP dispone con deskops review dispose sobre el recibo de esta tarea y la razón dice qué eligió en (1) y en (2). OUT: ejecutar cualquier cambio sin JP.

## Implementation Path

_Outline the expected implementation route or affected surface._



## Validation

_List the checks required before this task can close._

- deskops review status de esta tarea muestra la disposición de JP

## Done When

_Name the observable condition that makes the task complete._

JP dispone la decisión.

FILE:desk/rituals/phase.md
---
id: ritual-phase
steps: []
tags:
- workspace:desk
---

# Phase ritual for dependency-layer execution

Run one horizontal layer of scion tasks whose prerequisites are satisfied and whose
planned changes do not overlap, then close the layer with integration validation,
pill reconciliation, and next-phase preparation.

Each task in the phase still closes with its own validation and its own commit;
the phase adds the pass that only makes sense once those tasks are integrated.

FILE:desk/rituals/execution.md
---
id: ritual-execution
steps: []
tags:
- workspace:desk
---

# Execution ritual

Review the board, bind the relevant pills, keep scope tight, and implement only the active task for scion.

FILE:desk/rituals/testing.md
---
id: ritual-testing
steps: []
tags:
- workspace:desk
---

# Testing ritual

Run the smallest relevant validation first, then broaden coverage when scion changes shared behavior.

FILE:desk/rituals/closeout.md
---
id: ritual-closeout
steps: []
tags:
- workspace:desk
---

# Closeout ritual

Close a scion task only after validation passes, any durable knowledge from bound pills is linked to an atom when needed, the board is updated, and the final change is ready to commit.

FILE:instruccion
Cold-bundle de la tarea task-fase-0-ir-raíz-de-docker-en-el-ssd-y-docker-snap-o-no-snap-decisión-de-jp: con el TaskDoc, los rituales enrutados por el Board, las pills ligadas, los átomos ligados y los archivos que el TaskDoc nombra, reformula el encargo, lista ambigüedades con cita textual del input y da el DRY-RUN sin ejecutar nada. No ejecutes nada.

Sección de validación del TaskDoc:
- deskops review status de esta tarea muestra la disposición de JP

