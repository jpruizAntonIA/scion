# result-summary: tester de harness pi (imagen, .sldb, inventario de red)

- Tarea: `task-harness-pi-en-desk-real-red-bridge-para-ejecutores-imagen-con-pytest-dagster-spec2viz-sldb-en-el-wor`
- Rol: tester (`role-deskops-tester`), run `run-deskops-t-e2f0d5d6a151`, intento 1, herdr en robocop2 (no Scion)
- Qué se probó: el contrato tal como quedó tras el recorte del coordinador (los agentes en bridge pasaron a
  `task-ejecutores-pi-en-red-bridge-contra-el-listener-de-agentes-del-hub`), el diff sin commitear de `harnesses/pi/` y
  los artefactos del ejecutor en `runs/subagents/20261116-052313-harness-pi-red-bridge`.
- Evidencia: `validation.log` en este directorio, con cada comando, su salida y su exit. Corrí todo desde
  `/mnt/ssd/proyectos/SLDB_1/scion`, con `TMPDIR=/dev/shm`, un comando a la vez.

## Veredicto global: PASS

## Validaciones del contrato

| # | Validación | Resultado | Evidencia |
|---|---|---|---|
| V1 | `docker run --rm --entrypoint python3 scion-pi:f6e623c69 -c 'import pytest, xdist, dagster; print(...)'` imprime `9.2.0 3.8.0 1.13.24` | PASS | imprime `9.2.0 3.8.0 1.13.24`, exit 0 |
| V2 | `timeout 900 systemd-run --user --scope -q -p MemoryMax=2G -- python3 harnesses/pi/provision_test.py` | PASS | 19 tests OK, exit 0 |
| V3 | `cmp harnesses/scion_harness.py harnesses/pi/scion_harness.py` | PASS | exit 0 |
| V4 | `git diff --stat -- harnesses/` muestra solo Dockerfile y README.md | PASS | 2 archivos (+13, +7); `git status -- harnesses/` sin archivos nuevos |
| V5 | `grep -c 'ls_rc=0' mepu-sldb.txt` ≥ 1 y `make codigo-doc` con exit 0 | PASS | `1`; `make codigo-doc` → `exit: 0`; `git status --short` del worktree vacío después |
| V6 | `test -s propuesta-endpoint-hub.md && test -s probe-red.txt` | PASS | exit 0 |
| V7 | `ls /dev/shm/scion-pi-lab /dev/shm/scion-pi-mepu-wt` falla y `worktree list` no lista el wt | PASS | ls exit 2 (no existen); `grep -c scion-pi-mepu-wt` = 0 (exit 1 de grep = sin coincidencias, que es lo esperado) |
| V8 | `docker ps -a --filter ancestor=scion-pi:f6e623c69 -q` vacío | PASS | 0 líneas |

## Revisiones extra del encargo

| # | Revisión | Resultado | Evidencia |
|---|---|---|---|
| R1 | La imagen `scion-pi:f6e623c69` corresponde al Dockerfile del diff | PASS | `docker history --no-trunc`: las capas `apt-get install python3-pip` y `pip install ... pytest==9.2.0 pytest-xdist==3.8.0 dagster==1.13.24 && python3 -c 'import ...'` son literalmente las líneas del diff; la base es `GIT_COMMIT=f6e623c6…`; la imagen se creó a las 02:27:56 y el Dockerfile se modificó por última vez a las 02:24:22, o sea que la imagen es posterior a la edición. Id `sha256:64f2f0799e7a`, el mismo que reporta el ejecutor |
| R2 | El diff no toca nada fuera de `harnesses/pi/Dockerfile` y `README.md` | PASS | `git diff -- harnesses/pi/` es byte a byte igual a `harness-pi.diff` del ejecutor. El resto del árbol sucio son solo `desk/`, `.sldb/` y `runs/subagents/` (grep negativo sin coincidencias), del coordinador. Nada staged. El commit local adelantado `b834c57ab` solo toca `desk/` y `.sldb/` |
| R3 | La propuesta cita archivos y líneas que existen (abrí 4 citas) | PASS (con una imprecisión menor) | `pkg/runtime/common.go:2098` = `func ResolveHostNetworking`, con las tres ramas que describe (FORCE, host.docker.internal, loopback); `cmd/server_container_hub.go:148` = `func computeContainerHubEndpoint`; `cmd/server_helpers.go:84` = `func containerBridgeEndpoint`, que pone `host.docker.internal` en la línea 90; `cmd/server_web_base_url.go:160-170` contiene el texto exacto del error de dev-auth (`devAuthBindError`, línea 165). Esos cuatro archivos son idénticos en `f6e623c69` y en HEAD |

## Hallazgos

1. **Cita menor imprecisa.** La propuesta dice `cmd/server_web_base_url.go:160-170` `webStartupPreflight`. Ese rango
   es `devAuthBindError` (línea 165), que tiene el texto del error. `webStartupPreflight` empieza en la línea 177. El
   contenido es correcto y no bloquea.
2. **El `validation.log` del ejecutor deja vacío el `server.log`** de los dos intentos del hub de lab. Los textos de
   error de los guards aparecen en la propuesta y en result-summary, pero no en el log. No los pude reproducir sin
   arrancar un hub, y eso me está prohibido. Sí confirmé que el texto de dev-auth existe en el código de `f6e623c69`
   (R3). El texto del guard de base URL no https no lo verifiqué. Esta parte es inventario y no tiene validación
   ejecutable en el contrato, así que no bloquea.
3. **La imagen está en docker pero no en el repo.** `harnesses/pi/config.yaml` sigue con `image: scion-pi:latest`. El
   ejecutor ya lo anotó, y el contrato deja config.yaml fuera de alcance.
4. **El árbol tiene cambios ajenos al diff** (`desk/`, `.sldb/`, `runs/`) y un commit local sin pushear
   (`b834c57ab`, solo desk). El closeout debe commitear solo `harnesses/pi/Dockerfile` y `README.md` con rutas sueltas.
5. **Tests viejos o faltantes:** ningún test cubre el Dockerfile. El smoke de import del build y V1 son la única
   prueba, y alcanzan para el contrato.

## Guardrails probados

- No se tocaron `provision.py`, `provision_test.py` ni `config.yaml` (V4).
- No quedan contenedores de la imagen (V8) ni restos en /dev/shm (V7, L1).
- Este tester no arrancó hub, server ni agentes, no tocó `~/.scion`, ufw ni :8080, no creó worktrees y no escribió
  fuera de su run_dir. Usé un script auxiliar en el scratchpad de la sesión, fuera del repo.
- Que el hub de producción no se tocó solo lo puedo afirmar por el reporte del ejecutor. No lo verifiqué más allá
  de no tocarlo yo.

## Follow-up

- Closeout del coordinador: commitear el diff de `harnesses/pi/` (Dockerfile y README.md).
- Corregir la cita del hallazgo 1 si la propuesta se lleva a la task.decision del endpoint (opcional).
