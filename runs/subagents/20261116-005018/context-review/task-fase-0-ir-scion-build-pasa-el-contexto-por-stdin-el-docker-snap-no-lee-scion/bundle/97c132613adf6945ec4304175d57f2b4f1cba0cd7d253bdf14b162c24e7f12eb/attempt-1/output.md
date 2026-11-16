REFORMULACION
Propósito: desbloquear en el desk de IR la construcción de imágenes harness con scion cuando el CLI docker es snap y no puede leer `~/.scion`. Resultado: `scion build <harness-config>` empaqueta el directorio del harness-config en tar y lo pasa por stdin a docker (`-`), mientras podman y Apple container conservan el directorio como argumento; `--dry-run` muestra el comando equivalente; se añaden `localBuildArgs`/`writeBuildContextTar` y tests. Repo: scion, tocando `cmd/build.go` (rama local) y añadiendo `cmd/build_context.go` y `cmd/build_context_test.go`. Límites: fuera cloud-build, la configuración del docker de la máquina (decisión de JP) y otros comandos.

AMBIGUEDADES
1. Cita: "docker recibe un stream truncado, el build termina con error y scion devuelve 'build failed: ...'; el error del empaquetado es 'pack build context <dir>: <causa>'". Obliga a inventar si se espera/cierra la goroutine, cómo se propaga el error de empaquetado frente al de build y cómo se evita bloquear si docker no consume stdin.
2. Cita: "--dry-run imprime literalmente 'tar -C <hcDir.Path> -cf - . | ' + 'docker ' + argv unidos por espacios". Solo describe docker; obliga a inventar la salida para podman/Apple container.
3. Cita: "un archivo nuevo cmd/build_context.go". El bundle ya trae ese archivo implementado; obliga a inventar si el ejecutor debe crearlo, verificarlo o reescribirlo.

DRY-RUN
Lecturas: TaskDoc, rituales execution/testing/closeout, `cmd/build.go`, `cmd/build_context.go` y su test; pills/átomos: ninguno ligado. Cambios previstos: según Implementation Path, limitados a build.go y build_context{,_test}.go (condicionado a ambigüedad 3). Dependencias: `config.FindHarnessConfigDir`, `runtime.DetectContainerRuntime`, `io.Pipe`/`archive/tar`, docker snap en robocop2. Validaciones futuras: `go test ./cmd -run 'TestLocalBuildArgs|TestWriteBuildContextTar' -count=1`; `--dry-run` con binario del fork; build real con docker snap (rc 0 e imagen visible). Todo hipotético, sin ejecutar.

FUTURO
JP decide si cambia docker no-snap o su raíz; otro nodo implementa/valida y hace commit; el Board actualiza estado; la comprobación en robocop2 requiere máquina real.
