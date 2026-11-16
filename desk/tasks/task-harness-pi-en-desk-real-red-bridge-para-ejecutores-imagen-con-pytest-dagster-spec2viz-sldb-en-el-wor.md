---
sldb:
  by: agent
  at: '2026-11-16T05:20:10Z'
  authority: generated
  via: save_document_payload
id: task-harness-pi-en-desk-real-red-bridge-para-ejecutores-imagen-con-pytest-dagster-spec2viz-sldb-en-el-wor
status: draft
summary: ''
tags:
- workspace:desk
- artifact:task
- host:robocop2
current_node: ritual-execution
history: []
references:
- harnesses/pi/Dockerfile
- 4f3108cd8
- https://github.com/heyantonia/mepu/pull/246
depends_on: []
pills: []
files:
- harnesses/pi/Dockerfile
- harnesses/pi/README.md
- harnesses/pi/config.yaml
- harnesses/pi/provision.py
- harnesses/pi/provision_test.py
task_type: task.code
inherits_from: []
inherit_acceptance_context: false
atoms: []
from_drawer: desk/drawer/tasks/task-harness-pi-en-desk-real-red-bridge-para-ejecutores-imagen-con-pytest-dagster-spec2viz-sldb-en-el-worktree.md
---

# Harness pi en desk real: red bridge para ejecutores, imagen con pytest/xdist/dagster (spec2viz fuera por G7), .sldb en el worktree

## Rationale

_Explain why this task exists or the business driver behind it._

Primer piloto del harness pi en un desk real (mepu, 2026-11-11: DOC-12, 2 commits, 92 tests verdes; heyantonia/mepu#246). Con el Hub en loopback los ejecutores corren con --network=host y uno llegó a mepu_test con datos reales. La imagen no trae las herramientas del desk y el worktree de tarea no trae .sldb.

## Goal

_Describe the concrete result this task must produce._

Los ejecutores pi corren en red bridge sin alcanzar servicios del host, con la imagen ya equipada para los desks de SLDB_1 y con el store .sldb disponible en su worktree de tarea.

## Scope

_State what is in scope and what is out of scope._

IN, por prioridad: (1) PRIORIDAD: red bridge para ejecutores pi (sin --network=host ni SCION_FORCE_HOST_NETWORK), probada DESDE DENTRO del contenedor contra el gateway del bridge docker de esta máquina, 172.17.0.1 (docker network inspect bridge | grep Gateway): 127.0.0.1:15432 (Postgres local), 172.17.0.1:15432 y 172.17.0.1:8000 (descarga-adjuntos) deben fallar; el hub de lab debe responder. Hub de lab: una instancia efímera aparte del binario del fork /mnt/ssd/herramientas/scion-fork/f6e623c69/scion, con HOME=/dev/shm/scion-pi-lab/home (nunca ~/.scion), arrancada con server start --host 172.17.0.1 --web-port 18080 --enable-hub=true --enable-runtime-broker=true --enable-web=true --dev-auth=true y el proyecto /home/robocop/lab-scion (ruta absoluta: con HOME cambiado, ~ no sirve); se detiene con server stop y se borra /dev/shm/scion-pi-lab al terminar. "Responde" = curl -s -o /dev/null -w '%{http_code}' http://172.17.0.1:18080/ desde el contenedor devuelve un código HTTP distinto de 000. Si los servicios del host en 0.0.0.0 siguen alcanzables por 172.17.0.1 aun en bridge, NO se aplica ninguna regla de firewall (requiere sudo, es de JP): se anota el resultado del probe y la regla iptables concreta en la propuesta. El hub de producción (:8080) es la tarea task.decision hermana de JP y esta tarea NO lo toca. (2) pytest 9.2.0, pytest-xdist 3.8.0 (versiones del venv /mnt/ssd/proyectos/SLDB_1/.venv) y dagster 1.13.24 (la de requirements.txt de mepu) instalados en la imagen pi; hoy el ejecutor arma un venv en /tmp. spec2viz queda FUERA: JP aceptó su archivo (G7, 2026-11-15, deskops 80d32903). (3) Verificar que un worktree de tarea de mepu trae .sldb: desde el cambio de layout de sldb (c420809c, 2026-11-04) mepu versiona .sldb/store.yaml y .sldb/core/ (su .gitignore solo ignora .sldb_cache/ y .sldb/runtime/). Worktree: git -C /mnt/ssd/proyectos/mepu-scion/mepu worktree add --detach /dev/shm/scion-pi-mepu-wt HEAD, montado en el contenedor; al terminar git worktree remove /dev/shm/scion-pi-mepu-wt sin --force. Si no trae .sldb, se reporta como hallazgo, no se implementa copia. OUT: commitear o pushear (el ejecutor deja los cambios sin commitear; el coordinador los commitea con closeout y pushea), credenciales, cambios en otros harnesses, datos reales de mepu, spec2viz, reglas de firewall, reiniciar o reconfigurar el hub de producción en :8080.

## Implementation Path

_Outline the expected implementation route or affected surface._

Evidencia en un run-dir fijo que el ejecutor crea al empezar, relativo a la raíz de este repo (/mnt/ssd/proyectos/SLDB_1/scion): runs/subagents/<YYYYMMDD-HHMMSS>-harness-pi-red-bridge/ (en adelante RUN). Partir del bundle harnesses/pi que ya está en main (merge 4f3108cd8 de wt/pi-harness 7163525f9). Todo el lab corre con B=/mnt/ssd/herramientas/scion-fork/f6e623c69/scion, HOME=/dev/shm/scion-pi-lab/home y SCION_HUB_ENDPOINT=http://172.17.0.1:18080 exportados (nunca ~/.scion ni el hub de :8080). Pasos: (a) Imagen: agregar a harnesses/pi/Dockerfile, en un RUN pip install, pytest==9.2.0 pytest-xdist==3.8.0 dagster==1.13.24; en harnesses/pi/README.md agregar esas tres herramientas a la lista de lo que trae la imagen. provision.py y provision_test.py NO se tocan (la mejora es solo de imagen). Hub de lab: $B server start --host 172.17.0.1 --web-port 18080 --enable-hub=true --enable-runtime-broker=true --enable-web=true --dev-auth=true --auto-provide=true. Luego $B harness-config install file:///mnt/ssd/proyectos/SLDB_1/scion/harnesses/pi y $B build pi --base-image ghcr.io/jpruizantonia/scion-base:f6e623c69 --tag f6e623c69 (la imagen resultante es scion-pi:f6e623c69, que es la 'imagen pi nueva' de las validaciones; scion build actualiza el campo image del config.yaml instalado en el HOME del lab, no el de harnesses/pi del repo). (b) Red: /home/robocop/lab-scion ya es un proyecto scion (/home/robocop/lab-scion/.scion/project-id 71fb8717-4771-4ad1-8ec8-2f6575b21411); lanzar $B start pi-bridge-probe --harness pi --project /home/robocop/lab-scion --non-interactive (sin prompt; si el arranque falla por falta de la clave de DeepSeek en el hub de lab, se anota como bloqueo de JP en RUN/probe-red.txt y el probe se corre igual en un contenedor de la misma imagen en bridge, docker run --rm --network bridge --entrypoint bash scion-pi:f6e623c69 -c con el mismo probe, marcando en el archivo que no lo lanzó scion; ese contenedor de respaldo NO satisface la validación de NetworkMode, así que en ese caso la tarea se reporta bloqueada por la clave y no se cierra). Ubicar el contenedor con docker ps | grep pi-bridge-probe y correr el probe con docker exec <contenedor> bash -c con exactamente este probe, una línea por destino: for hp in 127.0.0.1/15432 172.17.0.1/15432 172.17.0.1/8000; do timeout 3 bash -c "echo > /dev/tcp/$hp" && echo "$hp ABIERTO" || echo "$hp cerrado"; done; curl -s -o /dev/null -w '%{http_code}' http://172.17.0.1:18080/ (el hub de lab responde si el código no es 000); salida a RUN/probe-red.txt, más docker inspect del contenedor. Inventariar en cmd/ y pkg/ de este repo cómo scion decide la red (SCION_FORCE_HOST_NETWORK, endpoint loopback) y citarlo en la propuesta. (c) Propuesta RUN/propuesta-endpoint-hub.md: hoy el hub de producción arranca con ~/.local/bin/scion y los argumentos de ~/.scion/server-args.json (server start --foreground --enable-hub=true --enable-runtime-broker=true --enable-web=true --dev-auth=true --auto-provide=true --web-assets-dir=...), sin --host, o sea en loopback (modo workstation, 127.0.0.1). Opciones: agregar --host 172.17.0.1 a esos argumentos, u otra que el inventario justifique; para cada una: riesgo (quién más alcanza :8080, --dev-auth expuesto en el bridge), comandos de aplicación (scion server stop; server start con los argumentos + --host) y vuelta atrás (los argumentos originales); y la regla iptables concreta si el probe mostró 172.17.0.1:15432 o :8000 alcanzables. (d) .sldb: git -C /mnt/ssd/proyectos/mepu-scion/mepu worktree add --detach /dev/shm/scion-pi-mepu-wt HEAD; $B start pi-mepu-sldb --harness pi --project /home/robocop/lab-scion -w /dev/shm/scion-pi-mepu-wt --non-interactive; docker exec <contenedor> bash -c 'cd /workspace && ls .sldb/core && command -v sldb && make codigo-doc' (make codigo-doc es el target de /mnt/ssd/proyectos/mepu-scion/mepu/Makefile, línea 180: corre sldb selfdoc python-sync y python-check sobre src/ con --store .sldb, así que necesita el CLI sldb y el store .sldb del worktree). Si sldb no está en el PATH del contenedor (lo pone el hook deskops-tools del proyecto de producción, que el lab no tiene), se anota y make codigo-doc se corre en /dev/shm/scion-pi-mepu-wt en el host como sustituto; ese sustituto con exit 0 satisface la validación (3), porque lo que se prueba es que el worktree trae un .sldb usable. Salida a RUN/mepu-sldb.txt. (e) Limpieza: $B stop y $B delete de pi-bridge-probe y pi-mepu-sldb, $B server stop, rm -rf /dev/shm/scion-pi-lab, git -C /mnt/ssd/proyectos/mepu-scion/mepu worktree remove /dev/shm/scion-pi-mepu-wt (sin --force); la imagen scion-pi:f6e623c69 se conserva (la usan los ejecutores pi).

## Validation

_List the checks required before this task can close._

- RUN/probe-red.txt (probe desde dentro del contenedor pi en bridge): 127.0.0.1:15432, 172.17.0.1:15432 y 172.17.0.1:8000 fallan (rechazo o timeout) y el curl a http://172.17.0.1:18080/ da un código HTTP distinto de 000; si 172.17.0.1:15432 o :8000 responden, RUN/propuesta-endpoint-hub.md trae la regla de firewall concreta para JP
- docker inspect <contenedor del ejecutor> | grep -c '"NetworkMode": "host"' imprime 0
- docker run --rm --entrypoint python3 scion-pi:f6e623c69 -c 'import pytest, xdist, dagster; print(pytest.__version__, dagster.__version__)' imprime 9.2.0 1.13.24
- RUN/mepu-sldb.txt: en /dev/shm/scion-pi-mepu-wt montado como /workspace con scion start -w: ls .sldb/core termina en 0 y make codigo-doc termina en exit 0, dentro del contenedor o, si sldb no está en su PATH, en el worktree en el host (sustituto válido, anotado)
- TMPDIR=/dev/shm timeout 900 systemd-run --user --scope -q -p MemoryMax=2G -- python3 harnesses/pi/provision_test.py pasa
- cmp harnesses/scion_harness.py harnesses/pi/scion_harness.py
- test -s RUN/propuesta-endpoint-hub.md
- Limpieza: ls /dev/shm/scion-pi-lab /dev/shm/scion-pi-mepu-wt falla (no existen) y git -C /mnt/ssd/proyectos/mepu-scion/mepu worktree list no lista /dev/shm/scion-pi-mepu-wt

## Done When

_Name the observable condition that makes the task complete._

Las mejoras (1) y (2) están en el árbol de trabajo de main de este repo, listas para que el coordinador las commitee; RUN tiene probe-red.txt, mepu-sldb.txt y propuesta-endpoint-hub.md; el ejecutor pi corrió en bridge (NetworkMode distinto de host) contra el hub de lab no loopback; la imagen pi importa pytest 9.2.0, xdist y dagster 1.13.24; hub de lab, /dev/shm/scion-pi-lab y el worktree de mepu ya no existen; el hub de producción no se tocó. Si la clave de DeepSeek falta en el hub de lab, la tarea no cumple este done_when: queda bloqueada con el probe de respaldo como evidencia.
