---
sldb:
  by: agent
  at: '2026-11-16T00:52:46Z'
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

- Precondición: git -C /mnt/ssd/proyectos/SLDB_1/scion status --short no muestra cambios de código (cmd/, pkg/, hooks/, image-build/, harnesses/) y C = git rev-parse --short HEAD; si el commit de la fase 0 no existe, la tarea espera
- /mnt/ssd/herramientas/scion-fork/<C>/scion version muestra (commit <primeros 8 de C>)
- docker images --filter "reference=ghcr.io/jpruizantonia/*:<C>" lista core-base, scion-base y scion-claude (el tag :latest también existe pero la validación es por :<C>)
- grep -rn homebrew-scion /mnt/ssd/proyectos/SLDB_1/IR/.scion/templates/ir-executor/ no devuelve nada (template generado por la tarea hermana del template de IR)
- Comando de JP para el hub: los argumentos de ~/.scion/server-args.json son server start --foreground --enable-hub=true --enable-runtime-broker=true --enable-web=true --dev-auth=true --auto-provide=true --web-assets-dir=<web dist>; el informe los copia literales
- build-images.sh --target core-base|scion-base|scion-claude --dry-run ya se verificó (imprime un docker buildx build por step); si un step fallara, el informe lo anota y la tarea queda bloqueada

## Done When

_Name the observable condition that makes the task complete._

scion version del binario versionado y la etiqueta :<sha> de las tres imágenes coinciden con el mismo commit, y ninguna referencia de la configuración nueva apunta a ghcr.io/homebrew-scion.
