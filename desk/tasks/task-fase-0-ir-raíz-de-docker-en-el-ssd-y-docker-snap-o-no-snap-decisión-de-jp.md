---
sldb:
  by: agent
  at: '2026-11-16T00:54:39Z'
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

Al revisar la máquina (15-11) resultó que la raíz de docker YA está en el SSD: /etc/fstab monta /mnt/ssd/docker sobre /var/snap/docker/common/var-lib-docker (bind, desde el 6-11; df la muestra en /dev/sda1). Lo que queda en el HDD es la raíz vieja, /var/snap/docker/common/var-lib-docker.hdd (27-10), que ya no usa nadie. El docker snap además no lee directorios ocultos de $HOME (resuelto en scion build por stdin) y se actualiza solo: un snap refresh reinicia dockerd y, sin live-restore, para los contenedores de los agentes. Borrar datos y cambiar de docker son decisiones de JP (brief scion-piloto-ir, fase 0 punto 2).

## Goal

_Describe the concrete result this task must produce._

JP decide (1) si borra la raíz vieja de docker que quedó en el HDD y (2) si sigue con el docker snap o pasa a docker-ce, con la recomendación y los comandos exactos del informe reports/scion-piloto-ir-20261115.md.

## Scope

_State what is in scope and what is out of scope._

IN: dos decisiones independientes, cada una con su respuesta: (1) borrar la raíz vieja del HDD /var/snap/docker/common/var-lib-docker.hdd (la raíz en uso ya está en el SSD, no hay que moverla); (2) seguir con el docker snap (con snap refresh --hold y live-restore) o pasar a docker-ce de apt con data-root /mnt/ssd/docker. La recomendación y los comandos exactos de cada una están en la sección Fase 0 de /mnt/ssd/proyectos/SLDB_1/reports/scion-piloto-ir-20261115.md. Que el snap no lea directorios ocultos de $HOME ya no bloquea (scion build pasa el contexto por stdin, tarea hermana). Registro: owner JP (review-<task>-owner-1); JP dispone ese recibo con una razón que dice qué eligió en (1) y en (2). OUT: ejecutar cualquier cambio sin JP.

## Implementation Path

_Outline the expected implementation route or affected surface._



## Validation

_List the checks required before this task can close._

- deskops review status de esta tarea muestra la disposición de JP

## Done When

_Name the observable condition that makes the task complete._

JP dispone el recibo owner de esta tarea (review-task-fase-0-ir-raíz-de-docker-en-el-ssd-y-docker-snap-o-no-snap-decisión-de-jp-owner-1, que registra este worker de la fase 0 en el desk de scion) con una razón que responde (1) y (2); una respuesta parcial no cierra. La tarea hermana es task-fase-0-ir-scion-build-pasa-el-contexto-por-stdin-el-docker-snap-no-lee-scion. Si el informe no tuviera la sección Fase 0, la tarea queda bloqueada hasta que exista.
