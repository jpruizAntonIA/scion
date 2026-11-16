# result-summary — deskops-t-eb68704bb5de (tester, intento 1)

Tarea: task-fase-0-ir-scion-build-pasa-el-contexto-por-stdin-el-docker-snap-no-lee-scion
Rol: tester (deskops-tester), subagente local (no Scion). Run: runs/subagents/20261116-180814-stdin-build-testing.
Bajo prueba: f6e623c69 (cmd/build.go, cmd/build_context.go, cmd/build_context_test.go; sin cambios hasta HEAD,
`git diff --stat f6e623c69 HEAD -- <3 archivos>` vacío) y tests/test_go_build_context_suite.py (sin commitear).
Comandos y rc: validation.log. Salidas: *.out en este directorio.

## Veredicto global: PASS

| # | Validación | Resultado |
|---|---|---|
| a | `go test ./cmd -run 'TestLocalBuildArgs\|TestWriteBuildContextTar' -count=1 -v` | PASS, rc 0; el filtro selecciona 3 tests (StreamsContextOnlyForDocker, PacksRelativeTreeWithLinks, RefusesSpecialFiles), ninguno skip (a-go-test.out) |
| b | pytest tests/test_go_build_context_suite.py vía puente deskops.testing | PASS, rc 0, 1 passed en 14.8 s con caché caliente (b-pytest.out) |
| c | `scion version` = `scion dev (commit f6e623c6)`; `scion build pi --dry-run` | PASS, rc 0: `tar -C /home/robocop/.scion/harness-configs/pi -cf - . \| docker build --build-arg BASE_IMAGE=ghcr.io/jpruizantonia/scion-base:latest -t scion-pi:latest -`. Con `--platform linux/amd64 --tag x --base-image b:1`, `--platform` va antes de `-` (c-dryrun2.out). claude: rc 1 "does not contain a Dockerfile" (esperado) |
| d | build real con docker snap desde ~/.scion | PASS, rc 0; aparece `scion-stdin-probe:stdin-probe-t153935` en `docker images` (d-build.out, d-images.out) |
| e | revisión del test + negativos | PASS: sin shell; los 3 negativos fallan como se espera (e-negative.out, e-test_neg.py) |

## Detalle de d (build real)
- Control (el comportamiento anterior): `docker build -t ... ~/.scion/harness-configs/stdin-probe` -> rc 1,
  `open Dockerfile: no such file or directory` (transfiere 2B). El problema del snap se reproduce (d-control-dir.out).
- Harness-config desechable: `cp -a pi stdin-probe` bajo ~/.scion/harness-configs. En la copia cambié `image:` a
  `scion-stdin-probe:latest` para que la imagen de salida no fuera un tag de `scion-pi` (build.go toma el nombre de
  la imagen del campo image del config).
- Flags: `--global --hub http://127.0.0.1:9 --tag stdin-probe-t153935 --base-image scion-pi-fork:e9ba9e2`, stdin
  </dev/null, cwd = run_dir, nunca --push. Por qué: según build.go, tras el build solo se llama a
  `syncBuildToHub`, que únicamente imprime avisos (nunca cambia el rc). Lo apunté a un endpoint inexistente para que
  no subiera nada al hub local real (~/.scion/hub.db). Con `--global`, EnsureHubReady corre con SkipProjectLink y
  no genera ni guarda project_id. `--base-image` evita cargar settings (el Dockerfile de pi hace `FROM scion-pi-fork:e9ba9e2`
  e ignora BASE_IMAGE). Resultado: "Warning: could not sync to Hub: Local scion server is not running", rc 0.
- Prueba adicional del contenido del tar: puse en el Dockerfile de la copia `COPY config.yaml` + `COPY home/`.
  rc 0. Dentro de la imagen, el sha256 de config.yaml es igual al del host (1079ac4b…) y home/ llega completo, con
  dueño root (uid/gid 0) (d2-build-copy.out, d2-run.out).
- Limpieza: `docker rmi` de los 2 tags (rc 0; `docker images | grep stdin-probe` = 0). Borré
  ~/.scion/harness-configs/stdin-probe. `find ~/.scion -path '*stdin-probe*'` = 0. En hub.db, abierto en solo lectura,
  ninguna tabla ni columna contiene 'stdin-probe' (0 hits), así que no había registro del hub que borrar.
- Verificación: `cmp ~/.scion/harness-configs/pi/config.yaml pi-config.yaml.before` rc 0. Sin cambios en context.yaml,
  settings.yaml, pi/config.yaml, project-configs/ ni templates/ (8608 archivos con sha256 antes y después; diff rc 0).
  `scion-pi:latest` (ec20cb8c44b6) y `scion-pi:f6e623c69` intactas. No quedan archivos míos en /dev/shm.

## Detalle de e (revisión del test)
- `run_foreign_suite` usa `subprocess.run(argv, ...)` sin `shell=True` y el test pasa una lista: no hay shell.
- Negativos (.py temporal en /dev/shm/stdin-build-tester-yPRj, borrado, copia en e-test_neg.py), resultado 3 failed y 1 passed:
  - paquete inexistente -> FAIL "exit code 1" (como se esperaba);
  - ejecutable inexistente -> FAIL "executable or cwd not found" (como se esperaba);
  - `"./cmd/nonexistent_pkg_xyz; true"` -> FAIL (el `; true` no se interpreta, lo que prueba que no hay shell);
  - `-run NoSuchTestXYZ` -> PASS (vacuo: lo anoto como hallazgo, abajo).

## Contrato (Implementation Path) contra el código: cumple
argv de localBuildArgs; `-` solo con docker; `--platform` solo si no está vacío; sin -f; io.Pipe con
`pw.CloseWithError(writeBuildContextTar(...))`, `Stdin = pr` y `pr.Close()` tras Run; errores `build failed: ...`,
`pack build context <dir>: ...` y `build context <path>: unsupported file type <tipo>`; rutas relativas con '/' y
directorios con '/' final; symlink con Linkname = os.Readlink; uid/gid 0 sin nombres; el dry-run es literal; podman y
container sin prefijo tar.

## Hallazgos (ninguno bloquea)
1. Evidencia vacua posible: si el filtro `-run` deja de seleccionar tests (por ejemplo, si renombran un test), `go test` sale con rc 0 y
   tests/test_go_build_context_suite.py pasa sin probar nada. Hoy selecciona 3. Mejora opcional: usar `-v` y exigir
   `--- PASS: TestLocalBuildArgs` y `--- PASS: TestWriteBuildContextTar` en la salida, o comprobar que no aparezca
   "no tests to run".
2. El supuesto del brief de que `scion build` reescribe el campo image del config.yaml no se cumple en este
   código: build.go no escribe el config (solo lo dice el texto Long de la ayuda). Ese texto es anterior y queda fuera
   del alcance. El único efecto posterior es syncBuildToHub, que solo avisa.
3. Cobertura: la línea del dry-run (prefijo tar, y su ausencia con podman) y el camino por stdin/pipe no tienen test
   unitario. Los cubren c y d de forma manual.
4. Con caché frío en HDD, el ejecutor midió 502 s contra un timeout de 900. Con GOCACHE en /mnt/ssd tardó 15 s.
