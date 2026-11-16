---
sldb:
  by: agent
  at: '2026-11-16T03:38:33Z'
  authority: generated
  via: save_document_payload
# board-xxx
id: board-001
# Affected workspace or domain
scope: desk
# List of task-xxx paths
tasks:
- desk/tasks/task-harness-pi-en-desk-real-red-bridge-para-ejecutores-imagen-con-pytest-dagster-spec2viz-sldb-en-el-wor.md
- desk/tasks/task-fase-0-ir-scion-build-pasa-el-contexto-por-stdin-el-docker-snap-no-lee-scion.md
- desk/tasks/task-fase-0-ir-hook-pre-start-deskops-tools-instala-sldb-y-deskops-editables-desde-workspace.md
- desk/tasks/task-fase-0-ir-binario-de-scion-e-imágenes-del-mismo-commit-del-fork-registry-ghcr-io-jpruizantonia.md
- desk/tasks/task-fase-0-ir-template-del-ejecutor-de-ir-con-tmp-en-ram-lock-de-tests-compartido-y-tope-de-memoria.md
- desk/tasks/task-fase-0-ir-raíz-de-docker-en-el-ssd-y-docker-snap-o-no-snap-decisión-de-jp.md
# List of pill-xxx paths
pills:
- desk/contexts/pills.md
# List of ritual-xxx paths
rituals:
- desk/rituals/phase.md
- desk/rituals/execution.md
- desk/rituals/testing.md
- desk/rituals/closeout.md
# e.g., system:sldb, workspace:desk
tags:
- workspace:desk
---

# scion Board

## Purpose

_Explain what this board routes and why it exists._

Route the active execution set for scion.

## Notes

_Add short operational notes about the current routed set._

Bootstrap complete. Add active task docs under `desk/tasks/` and route them here.

## Task Details

_Generated from the task references above._

- Harness pi en desk real: red bridge para ejecutores, imagen con pytest/dagster/spec2viz, .sldb en el worktree [draft] - Los ejecutores pi corren en red bridge sin alcanzar servicios del host, con la imagen ya equipada para los desks de SLDB_1 y con el store .sldb disponible en su worktree de tarea.
- Fase 0 IR: scion build pasa el contexto por stdin (el docker snap no lee ~/.scion) [draft] - `scion build <harness-config>` construye con docker aunque el CLI de docker no pueda leer ~/.scion: scion empaqueta el directorio del harness-config como tar y lo pasa por stdin (`docker build ... -`). podman y Apple container conservan el directorio como argumento. `--dry-run` muestra el comando equivalente (`tar -C <dir> -cf - . | docker build ... -`).
- Fase 0 IR: hook pre-start deskops-tools instala sldb y deskops editables desde /workspace [draft] - hooks/pre-start-deskops.sh instala sldb y deskops con `uv tool install --editable` directamente desde $SCION_WORKSPACE/sldb y $SCION_WORKSPACE/deskops (por defecto /workspace), con sldb también editable dentro del venv de deskops (`--with-editable`). Un cambio en /workspace/sldb o /workspace/deskops se ve en el siguiente comando del agente sin reinstalar.
- Fase 0 IR: binario de scion e imágenes del mismo commit del fork (registry ghcr.io/jpruizantonia) [draft] - Un binario del fork compilado en el commit C (scion version muestra C) y las imágenes core-base, scion-base y scion-claude construidas desde el mismo C con image-build/scripts/build-images.sh --registry ghcr.io/jpruizantonia (tags :latest y :<sha corto de C>). La versión queda anotada en reports/scion-piloto-ir-20261115.md. Activar el binario para el hub en :8080 (reemplazar ~/.local/bin/scion y reiniciar el servidor) y fijar image_registry en ~/.scion/settings.yaml son pasos de JP y quedan como comandos exactos en el informe.
- Fase 0 IR: template del ejecutor de IR con tmp en RAM, lock de tests compartido y tope de memoria [draft] - 1) deskops: `deskops add|edit|list|show role` y `... runtime-profile`; el --context-file de `deskops runtime template` acepta claves opcionales memory_limit, cpu_limit, shared_paths y env, que salen como resources.limits, volúmenes con la misma ruta y env en scion-agent.yaml. 2) Desk de IR: un RoleDoc del ejecutor (kind claude, con las reglas del brief dentro del rol) y un RuntimeProfileDoc claude, creados con deskops. 3) Template generado con deskops runtime template + context file (TMPDIR=/dev/shm, /dev/shm compartido, tope de memoria). 4) Medición: un test real de sldb que hace fsync, dentro del contenedor de la imagen del fork con esos montajes, dura < 2 s.
- Fase 0 IR: raíz de docker en el SSD y docker snap o no-snap (decisión de JP) [draft] - JP decide (1) si borra la raíz vieja de docker que quedó en el HDD y (2) si sigue con el docker snap o pasa a docker-ce, con la recomendación y los comandos exactos del informe reports/scion-piloto-ir-20261115.md.
