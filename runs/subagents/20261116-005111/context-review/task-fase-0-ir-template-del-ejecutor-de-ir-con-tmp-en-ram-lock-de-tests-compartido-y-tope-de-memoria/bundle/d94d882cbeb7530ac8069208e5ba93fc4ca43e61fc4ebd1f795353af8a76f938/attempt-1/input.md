FILE:desk/tasks/task-fase-0-ir-template-del-ejecutor-de-ir-con-tmp-en-ram-lock-de-tests-compartido-y-tope-de-memoria.md
---
sldb:
  by: agent
  at: '2026-11-16T00:48:52Z'
  authority: generated
  via: save_document_payload
id: task-fase-0-ir-template-del-ejecutor-de-ir-con-tmp-en-ram-lock-de-tests-compartido-y-tope-de-memoria
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
task_type: task.code
inherits_from: []
inherit_acceptance_context: false
atoms: []
---

# Fase 0 IR: template del ejecutor de IR con tmp en RAM, lock de tests compartido y tope de memoria

## Rationale

_Explain why this task exists or the business driver behind it._

Los ejecutores scion del piloto en IR tienen que correr tests con TMPDIR en RAM (el disco de docker está en el HDD lento), compartir /dev/shm/sldb1-tests.lock con el host (lo toman las suites completas y `sldb stores build --check`) y no pasar de un tope de memoria (31 GB en la máquina, 3-4 agentes como máximo). deskops runtime template no sabía emitir montajes extra, variables ni límites, y deskops no tenía cómo crear RoleDoc/RuntimeProfileDoc en un desk sin editar a mano.

## Goal

_Describe the concrete result this task must produce._

1) deskops: `deskops add|edit|list|show role` y `... runtime-profile`; el --context-file de `deskops runtime template` acepta claves opcionales memory_limit, cpu_limit, shared_paths y env, que salen como resources.limits, volúmenes con la misma ruta y env en scion-agent.yaml. 2) Desk de IR: un RoleDoc del ejecutor (kind claude, con las reglas del brief dentro del rol) y un RuntimeProfileDoc claude, creados con deskops. 3) Template generado con deskops runtime template + context file (TMPDIR=/dev/shm, /dev/shm compartido, tope de memoria). 4) Medición: un test real de sldb que hace fsync, dentro del contenedor de la imagen del fork con esos montajes, dura < 2 s.

## Scope

_State what is in scope and what is out of scope._

IN: deskops (models/role.py, models/runtime_profile.py, doc_access.py, cli/model_introspection.py, runtime/scion.py, sus tests y goldens de help), desk de IR solo vía deskops, el context file en .bootstrap/ de SLDB_1, la medición. OUT: código de IR, lanzar agentes scion (fase 1), cambiar el docker de la máquina.

## Implementation Path

_Outline the expected implementation route or affected surface._

deskops: __artifact__ en RoleDoc/RuntimeProfileDoc y registro en ARTIFACT_* y artifact_model_fields; _validate_container_keys en runtime/scion.py. Volúmenes extra: bind rw con source == target, sin opciones de propagación (scion los pasa como -v src:tgt). Context file /mnt/ssd/proyectos/SLDB_1/.bootstrap/ir-scion-context.json: project sldb-1, workspace_root /mnt/ssd/proyectos/SLDB_1, desk_root .../IR, source_root .../deskops, sldb_root .../sldb/src, memory_limit 6Gi, cpu_limit 2, shared_paths [/dev/shm], env {TMPDIR: /dev/shm}. IR: deskops add role --name ir-executor --kind claude con estas reglas en el body: todo en main sin worktrees; desk/ solo con deskops y .sldb/ solo con sldb; nunca reimplementar lo que sldb ya tiene; una suite completa por integración con TMPDIR=/dev/shm y tomando /dev/shm/sldb1-tests.lock; prohibido pkill y pgrep; no crear scripts encima de un CLI existente (lo que le falte a scion o deskops va con deskops message send --to scion|deskops); al terminar borrar lo propio de /dev/shm; nunca git add -A. deskops add runtime-profile --title 'Claude en scion' --kind claude --binary claude. Template: deskops runtime template role-ir-executor --root IR --harness claude --mode executor --task-repo IR --context-file <ese json>. Medición: sldb tests/store/test_io_atomic_write.py (escribe con os.fsync vía StoreIOUtils._atomic_write) dentro de un contenedor de ghcr.io/jpruizantonia/scion-claude:<C> con --memory 6g, -v /dev/shm:/dev/shm, TMPDIR=/dev/shm; en el host tarda 0.5 s en /dev/shm y 7.6 s en el HDD. Informe: sección Fase 0 de /mnt/ssd/proyectos/SLDB_1/reports/scion-piloto-ir-20261115.md.

## Validation

_List the checks required before this task can close._

- TMPDIR=/dev/shm python -m pytest -q tests/test_scion_runtime.py tests/test_role_runtime_artifacts.py tests/test_command_registry.py (de a uno, en deskops)
- TMPDIR=/dev/shm python -m pytest -q tests/test_output_goldens.py -k test_help_goldens (deskops)
- docker run con --memory=<tope>, -v /dev/shm:/dev/shm y TMPDIR=/dev/shm: el test de fsync de sldb dura < 2 s

## Done When

_Name the observable condition that makes the task complete._

Tests de deskops tocados en verde de a uno; IR/.scion/templates/ir-executor/scion-agent.yaml tiene resources.limits.memory, el volumen /dev/shm y TMPDIR; la medición de fsync queda < 2 s y anotada en el informe.

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
Cold-bundle de la tarea task-fase-0-ir-template-del-ejecutor-de-ir-con-tmp-en-ram-lock-de-tests-compartido-y-tope-de-memoria: con el TaskDoc, los rituales enrutados por el Board, las pills ligadas, los átomos ligados y los archivos que el TaskDoc nombra, reformula el encargo, lista ambigüedades con cita textual del input y da el DRY-RUN sin ejecutar nada. No ejecutes nada.

Sección de validación del TaskDoc:
- TMPDIR=/dev/shm python -m pytest -q tests/test_scion_runtime.py tests/test_role_runtime_artifacts.py tests/test_command_registry.py (de a uno, en deskops)
- TMPDIR=/dev/shm python -m pytest -q tests/test_output_goldens.py -k test_help_goldens (deskops)
- docker run con --memory=<tope>, -v /dev/shm:/dev/shm y TMPDIR=/dev/shm: el test de fsync de sldb dura < 2 s

