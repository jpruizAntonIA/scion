# result-summary: harness pi en desk real (red bridge, imagen, .sldb)

Ejecutor deskops-e-20f39328c207 (intento 1). Tarea
`task-harness-pi-en-desk-real-red-bridge-para-ejecutores-imagen-con-pytest-dagster-spec2viz-sldb-en-el-wor`.

## Estado: BLOQUEADA en la prioridad (1), red bridge. No cumple done_when.

Las partes (2) imagen y (3) .sldb están hechas y validadas. La parte (1) no se pudo probar como pide el contrato
porque el hub de lab no arranca en `172.17.0.1`. El bloqueo no es la clave de DeepSeek: son dos guards del propio
binario f6e623c69, que es el mismo commit que el de producción. Para hacerlo andar hay que cambiar código Go o el
despliegue (TLS y auth real), así que según las instrucciones queda como hallazgo y no lo implementé.

## Qué cambié (sin commitear)

Solo `harnesses/pi/Dockerfile` y `harnesses/pi/README.md`. No toqué `provision.py`, `provision_test.py` ni
`config.yaml`. Diff completo en `harness-pi.diff`:

- Dockerfile:
  - `apt-get install python3-pip`, porque scion-base no trae pip (Python 3.13, EXTERNALLY-MANAGED).
  - `pip install --no-cache-dir --break-system-packages --ignore-installed pytest==9.2.0 pytest-xdist==3.8.0 dagster==1.13.24`,
    con el mismo patrón y el mismo secreto `pipconf` que `harnesses/hermes/Dockerfile`.
  - Un smoke de import en el build.
- README: lista de las tres herramientas que trae la imagen.

## Qué corrí (todo en validation.log, con comando y exit)

| Validación | Resultado |
|---|---|
| imagen `scion-pi:f6e623c69` (`$B build pi --global --base-image …:f6e623c69 --tag f6e623c69`) | exit 0 (sha256:64f2f0799e7a) |
| `docker run --rm --entrypoint python3 scion-pi:f6e623c69 -c 'import pytest, xdist, dagster; …'` | `9.2.0 1.13.24`, exit 0 (xdist 3.8.0) |
| `TMPDIR=/dev/shm timeout 900 systemd-run … python3 harnesses/pi/provision_test.py` | 19 tests OK, exit 0 |
| `cmp harnesses/scion_harness.py harnesses/pi/scion_harness.py` | exit 0 |
| mepu-sldb.txt: `ls .sldb/core` con el worktree montado en /workspace (imagen pi, `--network none`) | ls_rc=0; `sldb` no está en el PATH del contenedor |
| mepu-sldb.txt: sustituto en el host, `make codigo-doc` en `/dev/shm/scion-pi-mepu-wt` | exit 0, worktree limpio después |
| probe-red.txt (probe de RESPALDO, `docker run --rm --network bridge`, no lanzado por scion) | 127.0.0.1:15432 cerrado (refused), 172.17.0.1:15432 cerrado, 172.17.0.1:8000 cerrado (timeout), curl :18080 → `000` |
| `docker inspect <ejecutor> \| grep -c '"NetworkMode": "host"'` | NO EJECUTADA: no hubo agente scion |
| `test -s propuesta-endpoint-hub.md` | exit 0 |
| limpieza: ls de `/dev/shm/scion-pi-lab` y `/dev/shm/scion-pi-mepu-wt` | ambos no existen (exit 2); `worktree list` sin el wt |

## Desvíos del contrato (anotados)

1. **Hub de lab: no arranca.**
   - Intento 1, comando del contrato más `--runtime-broker-port 19800` (sin él chocaría con el broker de
     producción en 127.0.0.1:9800): `dev auth cannot be enabled when the server is bound to a non-loopback address (172.17.0.1)`.
   - Intento 2, con `--dev-auth=false`: `refusing to start the web server: its base URL http://localhost:18080 … is not https, and it listens on 172.17.0.1:18080`.
   - No intenté más variantes: TLS, OAuth o un proxy que expusiera dev-auth serían inventar o saltarse un guard de
     seguridad.
2. **`harness-config install` exige hub**, incluso sin `SCION_HUB_ENDPOINT` ("No hub selected"). Para construir la
   imagen copié los archivos de `harnesses/pi` sobre el `pi` sembrado en
   `/dev/shm/scion-pi-lab/home/.scion/harness-configs/pi` (el HOME efímero del lab, no `~/.scion`) y usé
   `scion build pi --global`.
3. **`.sldb` sin `scion start -w`**, porque no había hub. Lo verifiqué montando el mismo worktree en la imagen pi
   con `docker run --rm --network none`, más el sustituto en el host que permite el contrato.
4. **`$B server stop` no se corrió, a propósito.** El daemon de lab nunca quedó arriba: no hay PID file y 18080/19800
   están libres. Sin PID file, `server stop` sondea los puertos por defecto 8080/9800, que son los del **hub de
   producción**, y ofrece matarlos (`cmd/server_daemon.go:313-336`). Correrlo habría puesto en riesgo producción.

## Hallazgos para el coordinador y JP

- **La decisión "hub de producción a `--host 172.17.0.1`" deja producción caída si se aplica tal cual.**
  `~/.local/bin/scion` es `commit f6e623c6` y trae los dos guards (los strings están en el binario). El análisis, las
  opciones y los comandos de aplicación y vuelta atrás están en `propuesta-endpoint-hub.md`.
- **ufw está activo con `DEFAULT_INPUT_POLICY="DROP"`.** Desde el bridge, `172.17.0.1:8000` (escucha en 0.0.0.0) y
  `:15432` hacen timeout, así que los servicios del host ya quedan aislados del bridge sin una regla nueva. Por lo
  mismo, un hub en 172.17.0.1 necesitará `sudo ufw allow in on docker0 to 172.17.0.1 port 8080 proto tcp` (JP). No
  pude leer las reglas actuales (root).
- **mepu no versiona `.sldb/store.yaml`.** En HEAD 58bf2607 (dev) solo están `.sldb/core/` (models, documents,
  store_index.yaml), al revés de lo que dicen el contrato y el comentario de su `.gitignore` (línea 40). Aun así,
  `make codigo-doc` termina en 0 con el `.sldb` del worktree, o sea que el store es usable. Lo reporto, no copié nada.
- `sldb` no está en el PATH de la imagen pi; en producción lo pone el hook deskops-tools.
- El build deja el warning `InvalidDefaultArgInFrom` (ARG BASE_IMAGE sin default). Ya existía y no lo toqué.
- La imagen `scion-pi:f6e623c69` queda en docker (la usan los ejecutores pi). El config.yaml instalado en el HOME
  del lab se borró con el lab. `harnesses/pi/config.yaml` del repo sigue con `image: scion-pi:latest`.

## Limpieza

- Ningún agente scion ni contenedor de este run quedó vivo: los `docker run` fueron con `--rm` y
  `docker ps -a` muestra 0 contenedores de `scion-pi:f6e623c69`.
- `/dev/shm/scion-pi-lab` está borrado.
- El worktree de mepu se quitó con `git worktree remove`, sin `--force`.
- No hay archivos míos en /dev/shm.
- El hub de producción y `~/.scion` no se tocaron (solo leí `~/.scion/server-args.json`).

## Qué debe revisar el coordinador

1. El diff de `harnesses/pi/Dockerfile` y `README.md`. Está listo para el closeout aunque la tarea siga bloqueada,
   o se puede partir.
2. La decisión sobre el endpoint del hub (`propuesta-endpoint-hub.md`): pasa a JP. Es TLS + auth real + regla ufw,
   o un cambio Go en una tarea aparte.
3. Si se reabre la parte (1), el lab necesita un hub que cumpla los guards. Otra opción es una tarea de código que
   agregue un listener de solo Hub API para agentes en la IP del bridge.
4. El hallazgo de `.sldb/store.yaml` en mepu.
