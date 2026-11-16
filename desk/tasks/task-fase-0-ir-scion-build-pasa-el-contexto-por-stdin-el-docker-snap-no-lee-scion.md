---
sldb:
  by: agent
  at: '2026-11-16T03:39:17Z'
  authority: generated
  via: save_document_payload
id: task-fase-0-ir-scion-build-pasa-el-contexto-por-stdin-el-docker-snap-no-lee-scion
status: draft
summary: ''
tags:
- workspace:desk
- artifact:task
current_node: ritual-execution
history: []
references:
- f6e623c69
- cmd/build_context_test.go
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

hcDir se obtiene como hoy con config.FindHarnessConfigDir(name, projectPath). localBuildArgs(runtimeBin, baseImage, outputImage, platform, contextDir) devuelve (argv, contextOnStdin): argv = [build, --build-arg, BASE_IMAGE=<baseImage>, -t, <outputImage>] + [--platform, <platform>] solo si platform no está vacío + un último argumento: '-' si runtimeBin == 'docker' (contextOnStdin = true), si no contextDir (false). Sin -f: el Dockerfile está en la raíz del contexto. Con stdin: io.Pipe; una goroutine llama writeBuildContextTar(pw, hcDir.Path) y cierra con pw.CloseWithError(err); buildExec.Stdin = pr. Si el tar falla después de arrancar docker, docker recibe un stream truncado, el build termina con error y scion devuelve 'build failed: ...'; el error del empaquetado es 'pack build context <dir>: <causa>'. writeBuildContextTar: rutas relativas a hcDir.Path con '/' (directorios con '/' final), symlinks como entradas TypeSymlink cuyo Linkname es os.Readlink tal cual (sin resolver ni validar, igual que docker), uid/gid 0 sin nombres; fifo/socket/dispositivo -> error 'build context <path>: unsupported file type <tipo>'. --dry-run imprime literalmente 'tar -C <hcDir.Path> -cf - . | ' + 'docker ' + argv unidos por espacios, sin comillas (mismo estilo que la salida anterior). Tras buildExec.Run() se cierra pr: si docker sale sin leer todo stdin, el Write de la goroutine falla (io.ErrClosedPipe) y termina, sin bloquear; el error que devuelve scion es siempre el de docker ('build failed: ...'), y el de empaquetado llega a docker como stdin truncado. podman/container: el dry-run imprime '<bin> ' + argv unidos por espacios, sin prefijo tar (igual que antes). Estado: el código ya está en main (commit f6e623c69): el ejecutor lo verifica contra este contrato, no lo reescribe.

## Validation

_List the checks required before this task can close._

- cd scion && go test ./cmd -run 'TestLocalBuildArgs|TestWriteBuildContextTar' -count=1
- scion build <harness-config> --dry-run (binario del fork) imprime 'tar -C <dir> -cf - . | docker build ... -'
- scion build <harness-config> con docker snap termina con rc 0 y la imagen aparece en docker images

## Done When

_Name the observable condition that makes the task complete._

Los tests nuevos pasan y en robocop2 `scion build` del fork construye una imagen de harness desde ~/.scion/harness-configs sin copiar el contexto a mano.
