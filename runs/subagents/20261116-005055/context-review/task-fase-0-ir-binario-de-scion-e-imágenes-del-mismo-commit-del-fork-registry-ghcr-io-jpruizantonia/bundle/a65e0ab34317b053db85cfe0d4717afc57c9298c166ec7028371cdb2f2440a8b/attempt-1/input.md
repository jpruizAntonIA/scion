FILE:desk/tasks/task-fase-0-ir-binario-de-scion-e-imágenes-del-mismo-commit-del-fork-registry-ghcr-io-jpruizantonia.md
---
sldb:
  by: agent
  at: '2026-11-16T00:48:50Z'
  authority: generated
  via: save_document_payload
id: task-fase-0-ir-binario-de-scion-e-imágenes-del-mismo-commit-del-fork-registry-ghcr-io-jpruizantonia
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
task_type: task.external
inherits_from: []
inherit_acceptance_context: false
atoms: []
---

# Fase 0 IR: binario de scion e imágenes del mismo commit del fork (registry ghcr.io/jpruizantonia)

## Rationale

_Explain why this task exists or the business driver behind it._

En robocop2 ~/.local/bin/scion es v0.2.21 (release homebrew, commit 55b99305): no soporta bloques ready/delivery ni hooks de proyecto, y las imágenes en uso salen de ghcr.io/homebrew-scion. El piloto en IR exige binario e imágenes del mismo commit del fork y nunca ghcr.io/homebrew-scion (brief, fase 0 punto 5).

## Goal

_Describe the concrete result this task must produce._

Un binario del fork compilado en el commit C (scion version muestra C) y las imágenes core-base, scion-base y scion-claude construidas desde el mismo C con image-build/scripts/build-images.sh --registry ghcr.io/jpruizantonia (tags :latest y :<sha corto de C>). La versión queda anotada en reports/scion-piloto-ir-20261115.md. Activar el binario para el hub en :8080 (reemplazar ~/.local/bin/scion y reiniciar el servidor) y fijar image_registry en ~/.scion/settings.yaml son pasos de JP y quedan como comandos exactos en el informe.

## Scope

_State what is in scope and what is out of scope._

IN: compilar con make build (GOCACHE/GOMODCACHE en /mnt/ssd/cache), instalar el binario en una ruta versionada sin pisar ~/.local/bin/scion, construir las tres imágenes localmente (sin push). OUT: reiniciar el hub, push al registry, imágenes de otros harnesses, cambiar el docker de la máquina.

## Implementation Path

_Outline the expected implementation route or affected surface._

Checkout: /mnt/ssd/proyectos/SLDB_1/scion en main, después de commitear el código de la fase 0. C = git rev-parse --short HEAD en ese momento (se anota en el informe). Binario: GOCACHE=/mnt/ssd/cache/go-build GOMODCACHE=/mnt/ssd/cache/go-mod make build; install -D build/scion /mnt/ssd/herramientas/scion-fork/<C>/scion. Imágenes (de a una, sin push, builder local-docker por defecto): image-build/scripts/build-images.sh --registry ghcr.io/jpruizantonia --target core-base; luego --target scion-base; luego --target scion-claude (build-images.sh --help acepta step IDs individuales como target con local-docker). Informe: sección 'Fase 0' de /mnt/ssd/proyectos/SLDB_1/reports/scion-piloto-ir-20261115.md con una tabla commit / binario / imagen:tag / id de imagen, y los comandos de JP literales: (a) instalar el binario en ~/.local/bin/scion y reiniciar el hub en :8080 con los mismos argumentos de ~/.scion/server-args.json; (b) image_registry: ghcr.io/jpruizantonia en ~/.scion/settings.yaml (hoy dice ghcr.io/homebrew-scion).

## Validation

_List the checks required before this task can close._

- /mnt/ssd/herramientas/scion-fork/<C>/scion version muestra (commit <C>)
- docker images --filter reference=ghcr.io/jpruizantonia/* lista core-base, scion-base y scion-claude con tag <C>
- grep -rn homebrew-scion sobre el template generado del ejecutor de IR y sobre los comandos de JP del informe no devuelve nada

## Done When

_Name the observable condition that makes the task complete._

scion version del binario versionado y la etiqueta :<sha> de las tres imágenes coinciden con el mismo commit, y ninguna referencia de la configuración nueva apunta a ghcr.io/homebrew-scion.

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
Cold-bundle de la tarea task-fase-0-ir-binario-de-scion-e-imágenes-del-mismo-commit-del-fork-registry-ghcr-io-jpruizantonia: con el TaskDoc, los rituales enrutados por el Board, las pills ligadas, los átomos ligados y los archivos que el TaskDoc nombra, reformula el encargo, lista ambigüedades con cita textual del input y da el DRY-RUN sin ejecutar nada. No ejecutes nada.

Sección de validación del TaskDoc:
- /mnt/ssd/herramientas/scion-fork/<C>/scion version muestra (commit <C>)
- docker images --filter reference=ghcr.io/jpruizantonia/* lista core-base, scion-base y scion-claude con tag <C>
- grep -rn homebrew-scion sobre el template generado del ejecutor de IR y sobre los comandos de JP del informe no devuelve nada

