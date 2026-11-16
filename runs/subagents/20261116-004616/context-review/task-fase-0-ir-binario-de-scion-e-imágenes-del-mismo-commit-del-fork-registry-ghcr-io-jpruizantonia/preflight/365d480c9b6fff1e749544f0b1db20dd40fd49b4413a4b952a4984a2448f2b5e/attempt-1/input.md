FILE:desk/tasks/task-fase-0-ir-binario-de-scion-e-imágenes-del-mismo-commit-del-fork-registry-ghcr-io-jpruizantonia.md
---
sldb:
  by: agent
  at: '2026-11-16T00:45:35Z'
  authority: generated
  via: create_document
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

GOCACHE=/mnt/ssd/cache/go-build GOMODCACHE=/mnt/ssd/cache/go-mod make build; install -D build/scion /mnt/ssd/herramientas/scion-fork/<sha>/scion; image-build/scripts/build-images.sh --registry ghcr.io/jpruizantonia --target core-base|scion-base|scion-claude (de a una, IO avg60 < 30).

## Validation

_List the checks required before this task can close._

- /mnt/ssd/herramientas/scion-fork/<sha>/scion version muestra el commit <sha>
- docker images ghcr.io/jpruizantonia/* lista core-base, scion-base y scion-claude con tag <sha>

## Done When

_Name the observable condition that makes the task complete._

scion version del binario versionado y la etiqueta :<sha> de las tres imágenes coinciden con el mismo commit, y ninguna referencia de la configuración nueva apunta a ghcr.io/homebrew-scion.

FILE:instruccion
Preflight solo-TaskDoc de la tarea task-fase-0-ir-binario-de-scion-e-imágenes-del-mismo-commit-del-fork-registry-ghcr-io-jpruizantonia: reformula el encargo tal como lo leería un ejecutor sin ningún otro contexto, lista ambigüedades con cita textual del input y da el DRY-RUN sin ejecutar nada. No ejecutes nada.

