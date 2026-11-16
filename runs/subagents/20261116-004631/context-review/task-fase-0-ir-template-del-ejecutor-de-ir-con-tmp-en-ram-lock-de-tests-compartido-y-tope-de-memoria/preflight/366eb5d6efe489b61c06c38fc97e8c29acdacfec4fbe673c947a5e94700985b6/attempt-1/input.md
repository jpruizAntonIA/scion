FILE:desk/tasks/task-fase-0-ir-template-del-ejecutor-de-ir-con-tmp-en-ram-lock-de-tests-compartido-y-tope-de-memoria.md
---
sldb:
  by: agent
  at: '2026-11-16T00:45:37Z'
  authority: generated
  via: create_document
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

deskops: __artifact__ en RoleDoc/RuntimeProfileDoc y registro en ARTIFACT_*; _validate_container_keys en runtime/scion.py. IR: deskops add role/runtime-profile; deskops runtime template role-ir-executor --root IR --harness claude --mode executor --context-file .bootstrap/ir-scion-context.json.

## Validation

_List the checks required before this task can close._

- TMPDIR=/dev/shm python -m pytest -q tests/test_scion_runtime.py tests/test_role_runtime_artifacts.py tests/test_command_registry.py (de a uno, en deskops)
- TMPDIR=/dev/shm python -m pytest -q tests/test_output_goldens.py -k test_help_goldens (deskops)
- docker run con --memory=<tope>, -v /dev/shm:/dev/shm y TMPDIR=/dev/shm: el test de fsync de sldb dura < 2 s

## Done When

_Name the observable condition that makes the task complete._

Tests de deskops tocados en verde de a uno; IR/.scion/templates/ir-executor/scion-agent.yaml tiene resources.limits.memory, el volumen /dev/shm y TMPDIR; la medición de fsync queda < 2 s y anotada en el informe.

FILE:instruccion
Preflight solo-TaskDoc de la tarea task-fase-0-ir-template-del-ejecutor-de-ir-con-tmp-en-ram-lock-de-tests-compartido-y-tope-de-memoria: reformula el encargo tal como lo leería un ejecutor sin ningún otro contexto, lista ambigüedades con cita textual del input y da el DRY-RUN sin ejecutar nada. No ejecutes nada.

