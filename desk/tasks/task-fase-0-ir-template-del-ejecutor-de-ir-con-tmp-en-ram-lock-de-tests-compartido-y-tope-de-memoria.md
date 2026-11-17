---
sldb:
  by: agent
  at: '2026-11-17T01:23:06Z'
  authority: generated
  via: save_document_payload
id: task-fase-0-ir-template-del-ejecutor-de-ir-con-tmp-en-ram-lock-de-tests-compartido-y-tope-de-memoria
status: draft
summary: ''
tags:
- workspace:desk
- artifact:task
- host:robocop2
current_node: ritual-execution
history: []
references:
- https://github.com/jpcosec/opsys/commit/4a7707a5ce8a1ed373a0b1f61197faa1a86b479f
- https://github.com/jpcosec/opsys/commit/4c745c184d7797783f98294047d02687b616dad7
- https://github.com/jpcosec/opsys/commit/881e177adc7add0c8ae51384ff3381951f998dbd
- runs/subagents/20261116-180814-template-ir-testing/result-summary.md
- runs/subagents/20261116-180814-template-ir-lock-testing/result-summary.md
- desk/tasks/task-los-agentes-scion-toman-el-lock-de-tests-compartido-con-el-uid-del-host-protected-regular-2.md
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

Los ejecutores scion del piloto en IR tienen que correr tests con TMPDIR en RAM (medido el 15-11: el test de fsync de sldb tarda 0.27 s con TMPDIR en /dev/shm, 0.57 s en el /tmp del contenedor, cuya capa está en el SSD, y 7.4 s en el HDD del host), compartir /dev/shm/sldb1-tests.lock con el host (lo toman las suites completas y `sldb stores build --check`) y no pasar de un tope de memoria (31 GB en la máquina, 3-4 agentes como máximo). deskops runtime template no sabía emitir montajes extra, variables ni límites, y deskops no tenía cómo crear RoleDoc/RuntimeProfileDoc en un desk sin editar a mano.

## Goal

_Describe the concrete result this task must produce._

1) deskops: `deskops add|edit|list|show role` y `... runtime-profile`; el --context-file de `deskops runtime template` acepta claves opcionales memory_limit, cpu_limit, shared_paths y env, que salen como resources.limits, volúmenes con la misma ruta y env en scion-agent.yaml. 2) Desk de IR: un RoleDoc del ejecutor (kind claude, con las reglas del brief dentro del rol) y un RuntimeProfileDoc claude, creados con deskops. 3) Template generado con deskops runtime template + context file (TMPDIR=/dev/shm, /dev/shm compartido, tope de memoria). 4) Medición: un test real de sldb que hace fsync, dentro del contenedor de la imagen del fork con esos montajes, dura < 2 s.

## Scope

_State what is in scope and what is out of scope._

IN: deskops (models/role.py, models/runtime_profile.py, doc_access.py, cli/model_introspection.py, runtime/scion.py, sus tests y goldens de help), desk de IR solo vía deskops, el context file en .bootstrap/ de SLDB_1, la medición. OUT: código de IR, lanzar agentes scion (fase 1), cambiar el docker de la máquina. Convenciones: --name ir-executor da id role-ir-executor y el template va a IR/.scion/templates/ir-executor/ (nombre del rol). El brief es /mnt/ssd/proyectos/SLDB_1/scion-piloto-ir-brief.md; sus reglas van al body markdown del RoleDoc como lista. 'Una suite completa por integración' = una vez cada vez que el coordinador integra un cambio en main, con TMPDIR=/dev/shm y bajo /dev/shm/sldb1-tests.lock. El tope de la medición es el mismo del template: 6Gi (docker --memory 6g).

## Implementation Path

_Outline the expected implementation route or affected surface._

deskops: __artifact__ en RoleDoc/RuntimeProfileDoc y registro en ARTIFACT_* y artifact_model_fields; _validate_container_keys en runtime/scion.py. Volúmenes extra: bind rw con source == target, sin opciones de propagación (scion los pasa como -v src:tgt). Context file /mnt/ssd/proyectos/SLDB_1/.bootstrap/ir-scion-context.json: project sldb-1, workspace_root /mnt/ssd/proyectos/SLDB_1, desk_root .../IR, source_root .../deskops, sldb_root .../sldb/src, memory_limit 6Gi, cpu_limit 2, shared_paths [/dev/shm], env {TMPDIR: /dev/shm}. IR: deskops add role --name ir-executor --kind claude con estas reglas en el body: todo en main sin worktrees; desk/ solo con deskops y .sldb/ solo con sldb; nunca reimplementar lo que sldb ya tiene; una suite completa por integración con TMPDIR=/dev/shm y tomando /dev/shm/sldb1-tests.lock; prohibido pkill y pgrep; no crear scripts encima de un CLI existente (lo que le falte a scion o deskops va con deskops message send --to scion|deskops); al terminar borrar lo propio de /dev/shm; nunca git add -A. deskops add runtime-profile --title 'Claude en scion' --kind claude --binary claude. Template: deskops runtime template role-ir-executor --root IR --harness claude --mode executor --task-repo IR --context-file <ese json>. Medición: el archivo de test test_io_atomic_write de la carpeta store de los tests de sldb (escribe con os.fsync vía StoreIOUtils._atomic_write) dentro de un contenedor de ghcr.io/jpruizantonia/scion-claude:<C> con --memory 6g, -v /dev/shm:/dev/shm, TMPDIR=/dev/shm; en el host tarda 0.5 s en /dev/shm y 7.6 s en el HDD. Informe: sección Fase 0 de /mnt/ssd/proyectos/SLDB_1/reports/scion-piloto-ir-20261115.md.

## Validation

_List the checks required before this task can close._

- En el repo deskops (/mnt/ssd/proyectos/SLDB_1/deskops), de a uno con TMPDIR=/dev/shm: python -m pytest -q sobre los archivos de test test_scion_runtime, test_role_runtime_artifacts y test_command_registry (el contrato CLI de role/runtime-profile sale de los modelos y queda fijado en los goldens de help deskops_{add,edit,list,show}_{role,runtime-profile}.txt)
- En el repo deskops: el test test_help_goldens del archivo test_output_goldens pasa
- Medición: docker run --rm --memory 6g -v /dev/shm:/dev/shm -e TMPDIR=/dev/shm -v /mnt/ssd/proyectos/SLDB_1:/mnt/ssd/proyectos/SLDB_1 ghcr.io/jpruizantonia/scion-claude:f6e623c69, con cwd en la raíz del repo sldb (no src/), corre el archivo de test test_io_atomic_write de la carpeta store de sldb: debe durar < 2 s
- Lock, con el uid del host como corre el agente scion (sciontool lo remapea con SCION_HOST_UID; en el docker run de la prueba, --user 1001:1001): con el host sosteniendo flock /dev/shm/sldb1-tests.lock, flock -n /dev/shm/sldb1-tests.lock dentro del contenedor falla (rc 1); sin el host, toma el lock (rc 0). Como root falla con rc 66 (EACCES) por fs.protected_regular=2 del host: no es la condición que se prueba

## Done When

_Name the observable condition that makes the task complete._

Tests de deskops tocados en verde de a uno; IR/.scion/templates/ir-executor/scion-agent.yaml tiene resources.limits.memory, el volumen /dev/shm y TMPDIR; la medición de fsync queda < 2 s y anotada en el informe.
