FILE:desk/tasks/task-fase-0-ir-scion-build-pasa-el-contexto-por-stdin-el-docker-snap-no-lee-scion.md
---
sldb:
  by: agent
  at: '2026-11-16T00:45:30Z'
  authority: generated
  via: create_document
id: task-fase-0-ir-scion-build-pasa-el-contexto-por-stdin-el-docker-snap-no-lee-scion
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
files:
- cmd/build.go
- cmd/build_context.go
- cmd/build_context_test.go
task_type: task.code
inherits_from: []
inherit_acceptance_context: false
atoms: []
---

# Fase 0 IR: scion build pasa el contexto por stdin (el docker snap no lee ~/.scion)

## Rationale

_Explain why this task exists or the business driver behind it._

En robocop2 docker es snap (29.8.0) y su CLI no puede abrir directorios ocultos de $HOME; `scion build <harness-config>` falla con 'open Dockerfile: no such file or directory' porque le pasa ~/.scion/harness-configs/<name> como contexto. Bloquea construir imágenes de harness para el piloto scion en el desk de IR (brief scion-piloto-ir, fase 0 punto 2).

## Goal

_Describe the concrete result this task must produce._

`scion build <harness-config>` construye con docker aunque el CLI de docker no pueda leer ~/.scion: scion empaqueta el directorio del harness-config como tar y lo pasa por stdin (`docker build ... -`). podman y Apple container conservan el directorio como argumento. `--dry-run` muestra el comando equivalente (`tar -C <dir> -cf - . | docker build ... -`).

## Scope

_State what is in scope and what is out of scope._

IN: cmd/build.go (rama local, no cloud-build) y un archivo nuevo cmd/build_context.go con localBuildArgs y writeBuildContextTar, más cmd/build_context_test.go. Los symlinks del contexto se guardan como links (como hace docker); fifos/sockets/dispositivos se rechazan; uid/gid del host no viajan. OUT: cloud-build, la configuración del docker de la máquina (cambiar a docker no-snap o mover su raíz es decisión de JP), otros comandos.

## Implementation Path

_Outline the expected implementation route or affected surface._

localBuildArgs(runtimeBin, baseImage, outputImage, platform, contextDir) devuelve argv y si el contexto va por stdin (solo runtimeBin == docker). En RunE, con stdin: io.Pipe, una goroutine escribe writeBuildContextTar(pw, hcDir.Path) y cierra con el error; buildExec.Stdin = pr.

## Validation

_List the checks required before this task can close._

- cd scion && go test ./cmd -run 'TestLocalBuildArgs|TestWriteBuildContextTar' -count=1
- scion build <harness-config> --dry-run (binario del fork) imprime 'tar -C <dir> -cf - . | docker build ... -'
- scion build <harness-config> con docker snap termina con rc 0 y la imagen aparece en docker images

## Done When

_Name the observable condition that makes the task complete._

Los tests nuevos pasan y en robocop2 `scion build` del fork construye una imagen de harness desde ~/.scion/harness-configs sin copiar el contexto a mano.

FILE:instruccion
Preflight solo-TaskDoc de la tarea task-fase-0-ir-scion-build-pasa-el-contexto-por-stdin-el-docker-snap-no-lee-scion: reformula el encargo tal como lo leería un ejecutor sin ningún otro contexto, lista ambigüedades con cita textual del input y da el DRY-RUN sin ejecutar nada. No ejecutes nada.

