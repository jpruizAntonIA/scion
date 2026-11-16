REFORMULACION
Encargo ejecutable en el repo `scion` (fork; rutas `cmd/...`): hacer que `scion build <harness-config>` construya con Docker aunque su CLI no pueda leer `~/.scion`. Resultado: en la rama local de build, Docker recibe el directorio del harness-config como tar por stdin (`docker build ... -`); podman y Apple container mantienen el directorio como argumento; `--dry-run` muestra el comando equivalente. Límites: solo `cmd/build.go` (rama local, no cloud-build), nuevo `cmd/build_context.go` con `localBuildArgs` y `writeBuildContextTar`, y `cmd/build_context_test.go`. Fuera: cloud-build, configuración del Docker de la máquina y otros comandos.

AMBIGUEDADES
1. «Los symlinks del contexto se guardan como links (como hace docker); fifos/sockets/dispositivos se rechazan»: no define representación tar de symlinks, tratamiento de rutas absolutas/escapadas, ni mensaje, tipo y propagación del error al rechazar. Obligaría a inventar semántica y contrato de error.
2. «localBuildArgs(runtimeBin, baseImage, outputImage, platform, contextDir) devuelve argv» y «docker build ... -»: no fija nombres, orden ni presencia de flags (`-t`, `-f`, `--platform`, etc.). Obligaría a inventar el argv exacto.
3. «buildExec.Stdin = pr» y «hcDir.Path»: no define cómo se obtiene `hcDir` ni qué ocurre si el tar falla tras iniciar Docker. Obligaría a inventar integración y manejo de errores.
4. «scion build <harness-config> --dry-run ... imprime 'tar -C <dir> -cf - . | docker build ... -'»: el formato exacto y el escape de rutas quedan implícitos. Obligaría a inventar la salida literal.

DRY-RUN
Lecturas: TaskDoc, `cmd/build.go`, archivos nuevos previstos y definición de `hcDir`. Cambios: añadir `localBuildArgs` y `writeBuildContextTar`; en `RunE`, para Docker, crear `io.Pipe`, escribir el tar en goroutine y asignar `Stdin`; conservar argumento-directorio para otros runtimes; añadir tests. Dependencias: `archive/tar`, Docker snap, harness-config real. Validaciones futuras: `go test ./cmd -run 'TestLocalBuildArgs|TestWriteBuildContextTar' -count=1`; `--dry-run`; build real en robocop2 y comprobación en `docker images`.

FUTURO
JP decide si cambia el Docker snap o su raíz (fuera de alcance). Otro ejecutor debe aportar el nombre del harness-config y ejecutar las validaciones en robocop2; un nodo de integración/CI verificará tests y commit.
