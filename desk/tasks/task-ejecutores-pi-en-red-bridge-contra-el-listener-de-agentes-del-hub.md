---
sldb:
  by: agent
  at: '2026-11-16T05:40:38Z'
  authority: generated
  via: save_document_payload
id: task-ejecutores-pi-en-red-bridge-contra-el-listener-de-agentes-del-hub
status: draft
summary: ''
tags:
- workspace:desk
- artifact:task
- host:robocop2
current_node: ritual-execution
history: []
references:
- runs/subagents/20261116-052313-harness-pi-red-bridge/propuesta-endpoint-hub.md
depends_on:
- task-hub-de-scion-listener-de-solo-hub-api-para-agentes-en-la-ip-del-bridge-sin-web-ni-dev-auth
- task-regla-ufw-que-abre-en-docker0-solo-el-listener-de-agentes-del-hub-de-scion-acción-de-jp-con-sudo
pills: []
files:
- harnesses/pi/README.md
task_type: task.code
inherits_from: []
inherit_acceptance_context: false
atoms: []
---

# Ejecutores pi en red bridge contra el listener de agentes del hub

## Rationale

_Explain why this task exists or the business driver behind it._

Es la parte (1) de la tarea del harness pi, partida por el coordinador el 2026-11-16 porque el hub no puede escuchar en 172.17.0.1 tal como está (runs/subagents/20261116-052313-harness-pi-red-bridge/propuesta-endpoint-hub.md). Con el listener de agentes y la regla ufw, un ejecutor pi lanzado por scion debe correr en red bridge, alcanzar el hub y no alcanzar los servicios del host.

## Goal

_Describe the concrete result this task must produce._

Un agente pi lanzado por scion contra un hub de lab con --agent-api-host 172.17.0.1 --agent-api-port 18090 corre con NetworkMode distinto de host, alcanza el listener de agentes desde dentro del contenedor y no alcanza 127.0.0.1:15432, 172.17.0.1:15432 ni 172.17.0.1:8000. Con eso queda probada, en el lab, la configuración que JP aplicará en producción (puerto 8090).

## Scope

_State what is in scope and what is out of scope._

IN: solo evidencia en el run_dir del ejecutor y, si hace falta, harnesses/pi/README.md (una sección de red bridge). Hub de lab: binario construido desde main de este repo (ya con el listener de agentes), HOME efímero /dev/shm/scion-pi-bridge-lab (borrado al final), proyecto /home/robocop/lab-scion, --web-port 18080 --runtime-broker-port 19800 --agent-api-host 172.17.0.1 --agent-api-port 18090 y web en loopback; harness-config pi instalado en ese HOME; imagen scion-pi:f6e623c69. Si el agente no arranca por falta de la clave de DeepSeek en el hub de lab, es un bloqueo de JP: se anota, sin registrar claves. OUT: el hub de producción en :8080, ~/.scion, ufw y sudo (la regla es la task.decision de la que depende), cambios Go.

## Implementation Path

_Outline the expected implementation route or affected surface._

1) go build del binario desde main (GOCACHE=/mnt/ssd/cache/go-build GOMODCACHE=/mnt/ssd/cache/go-mod) en /dev/shm/scion-pi-bridge-lab/scion. 2) Con HOME=/dev/shm/scion-pi-bridge-lab/home y SCION_HUB_ENDPOINT=http://127.0.0.1:18080 exportados y SCION_FORCE_HOST_NETWORK sin definir: server start con los flags del scope, registrando su PID; harness-config install de harnesses/pi en ese HOME. 3) scion start pi-bridge-probe --harness pi --project /home/robocop/lab-scion --non-interactive. 4) docker exec <contenedor> bash -c con: for hp in 127.0.0.1/15432 172.17.0.1/15432 172.17.0.1/8000 172.17.0.1/18090; do timeout 3 bash -c "echo > /dev/tcp/$hp" && echo "$hp ABIERTO" || echo "$hp cerrado"; done; salida en probe-red.txt del run_dir, más docker inspect del contenedor. 5) Limpieza: scion stop y scion delete del agente, kill del PID registrado del server de lab (nunca scion server stop sin PID file, sondea los puertos de producción), rm -rf /dev/shm/scion-pi-bridge-lab.

## Validation

_List the checks required before this task can close._

- probe-red.txt del run_dir: 172.17.0.1/18090 ABIERTO y 127.0.0.1/15432, 172.17.0.1/15432 y 172.17.0.1/8000 cerrado, desde el contenedor de pi-bridge-probe lanzado por scion
- docker inspect <contenedor de pi-bridge-probe> | grep -c '"NetworkMode": "host"' imprime 0
- Limpieza: ls /dev/shm/scion-pi-bridge-lab falla, ss -ltn no lista 18080, 18090 ni 19800 y docker ps -a no lista pi-bridge-probe

## Done When

_Name the observable condition that makes the task complete._

Un agente pi lanzado por scion corrió en bridge, alcanzó el listener de agentes y no los servicios del host, con la evidencia en el run_dir; o, si faltó la clave de DeepSeek, el bloqueo quedó anotado y la tarea no se cierra. Nada del lab quedó vivo y el hub de producción no se tocó.
