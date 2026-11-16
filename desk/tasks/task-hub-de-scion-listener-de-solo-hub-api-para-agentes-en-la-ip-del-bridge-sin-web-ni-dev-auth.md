---
sldb:
  by: agent
  at: '2026-11-16T06:30:39Z'
  authority: generated
  via: save_document_payload
id: task-hub-de-scion-listener-de-solo-hub-api-para-agentes-en-la-ip-del-bridge-sin-web-ni-dev-auth
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
- fc771c045
- cmd/server_agent_api_test.go
- runs/subagents/20261116-054630-hub-agent-listener/result-summary.md
- runs/subagents/20261116-054630-hub-agent-listener-testing/result-summary.md
depends_on: []
pills: []
files:
- cmd/server.go
- cmd/server_foreground.go
- cmd/server_container_hub.go
- cmd/server_container_hub_test.go
- cmd/server_agent_api.go
- cmd/server_agent_api_test.go
task_type: task.code
inherits_from: []
inherit_acceptance_context: false
atoms: []
---

# Hub de scion: listener de solo Hub API para agentes en la IP del bridge, sin web ni dev-auth

## Rationale

_Explain why this task exists or the business driver behind it._

Los ejecutores pi corren con --network host porque el hub de producción escucha en loopback (pkg/runtime/common.go ResolveHostNetworking manda a red host todo endpoint localhost/127.0.0.1/::1 o host.docker.internal). Pasar el hub entero a --host 172.17.0.1 no arranca: el binario f6e623c69 rechaza dev-auth en un host no loopback y exige base URL https para la web (cmd/server_web_base_url.go webStartupPreflight). Evidencia y opciones: runs/subagents/20261116-052313-harness-pi-red-bridge/propuesta-endpoint-hub.md. JP delegó el 2026-11-16 en el coordinador elegir una vía que funcione; el coordinador eligió un listener aparte, solo para agentes, que no sirve la web ni acepta dev-auth, para que la web y el dev-auth sigan en loopback.

## Goal

_Describe the concrete result this task must produce._

scion server start acepta --agent-api-host <ip> y --agent-api-port <puerto>, que van juntos (uno solo es error de arranque con un mensaje que nombre ambos flags). Con ambos, el hub abre un http.Server extra en <ip>:<puerto> con el mismo handler de Hub API, detrás de un guard de solo agentes: /healthz, /health y /readyz responden sin auth; cualquier otro path exige un token de agente válido (lo que reconoce extractAgentToken en pkg/hub/auth.go: header X-Scion-Agent-Token o JWT de agente en Bearer) y, si no lo trae, da 401, incluso /api/v1/auth/* y los tokens scion_dev_*, scion_pat_* o de sesión web. Lo que un agente puede hacer sigue limitado por los scopes de su token (authz, sin cambios). No se sirve la web. computeContainerHubEndpoint usa el orden: runtime_broker.container_hub_endpoint configurado > listener de agentes > dominio público o IAP (lo de hoy) > host.docker.internal (lo de hoy). Sin los flags, el comportamiento es idéntico al actual.

## Scope

_State what is in scope and what is out of scope._

IN: cmd/server.go (flags), cmd/server_foreground.go (arranque del listener extra con el mismo handler de Hub API que el modo standalone, envuelto para rechazar dev-auth), cmd/server_container_hub.go (computeContainerHubEndpoint usa el listener de agentes cuando existe) y sus tests (cmd/server_container_hub_test.go y un test nuevo del listener en cmd/). Los guards actuales (dev-auth solo en loopback, web no https solo en loopback) NO se tocan ni se relajan: el listener de agentes no es la web. OUT: TLS, OAuth, ufw, sudo, el hub de producción en :8080 y ~/.scion (aplicar el flag en producción es posterior), cambios en pkg/runtime, la imagen pi y los harnesses.

## Implementation Path

_Outline the expected implementation route or affected surface._

1) Leer cmd/server.go (flags --host, --port, --web-port), cmd/server_foreground.go (cómo se arma el handler de Hub API en modo standalone vs con --enable-web, y applyServerListenHosts), cmd/server_container_hub.go (containerHubEndpointInputs y computeContainerHubEndpoint) y cmd/server_web_base_url.go (webStartupPreflight, para no relajar sus guards). 2) Agregar los flags y, si ambos están definidos, un http.Server extra en <agent-api-host>:<agent-api-port> con el handler de Hub API; el guard de solo agentes descrito en goal, delante del UnifiedAuthMiddleware que ya usa la Hub API (que valida el token de agente). 3) Agregar a containerHubEndpointInputs el endpoint del listener de agentes: Configured gana; si no, el listener de agentes; si no, lo de hoy. 4) Tests Go (httptest, sin red real): el guard deja pasar /healthz sin token, da 401 a /api/v1/auth/login, a un Bearer scion_dev_x y a un request sin token, y deja pasar un request con X-Scion-Agent-Token válido (fixture del AgentTokenSvc que ya usan los tests de pkg/hub o cmd); uno solo de los flags da error; computeContainerHubEndpoint con y sin listener de agentes y con Configured; el listener rechaza dev-auth (401) y sirve una ruta de la Hub API con token de agente; sin flags no se abre ningún listener extra. 5) Prueba en el host con un HOME efímero en /dev/shm/scion-agentapi-lab (borrado al final), el binario construido del árbol (go build -buildvcs=false -o /dev/shm/scion-agentapi-lab/scion ./cmd/scion, el MAIN_PKG del Makefile) y puertos que no choquen con producción (--web-port 18080 --runtime-broker-port 19800 --agent-api-host 172.17.0.1 --agent-api-port 18090, web en loopback): el server arranca y curl desde el host a http://172.17.0.1:18090/ no sirve la web. El server de lab se detiene matando solo su PID registrado (nunca scion server stop sin PID file: sondea 8080/9800 de producción), sin pkill ni pgrep. GOCACHE=/mnt/ssd/cache/go-build y GOMODCACHE=/mnt/ssd/cache/go-mod.

## Validation

_List the checks required before this task can close._

- cd /mnt/ssd/proyectos/SLDB_1/scion && GOCACHE=/mnt/ssd/cache/go-build GOMODCACHE=/mnt/ssd/cache/go-mod TMPDIR=/dev/shm go test ./cmd -run 'ContainerHubEndpoint|AgentAPI' -count=1
- cd /mnt/ssd/proyectos/SLDB_1/scion && GOCACHE=/mnt/ssd/cache/go-build GOMODCACHE=/mnt/ssd/cache/go-mod TMPDIR=/dev/shm go vet ./cmd
- Lab en el host, salida en agent-api-lab.txt del run_dir que asigna el coordinador: con --agent-api-host 172.17.0.1 --agent-api-port 18090 y la web en 127.0.0.1:18080, curl -s -o /dev/null -w '%{http_code}' a http://172.17.0.1:18090/healthz da 200; a http://172.17.0.1:18090/ da 401; a http://172.17.0.1:18090/api/v1/auth/login da 401; con -H 'Authorization: Bearer scion_dev_x' a http://172.17.0.1:18090/api/v1/agents da 401
- Con un solo flag (--agent-api-host sin --agent-api-port) el server de lab no arranca y el error nombra los dos flags; sin ninguno, ss -ltn no lista 18090
- Limpieza: ls /dev/shm/scion-agentapi-lab falla y ss -ltn no lista 18080, 18090 ni 19800

## Done When

_Name the observable condition that makes the task complete._

Los flags existen, el listener de agentes sirve solo Hub API y rechaza dev-auth, computeContainerHubEndpoint devuelve su URL cuando no hay endpoint configurado, los tests Go nuevos y existentes de ./cmd del filtro pasan, go vet ./cmd limpio, la prueba de lab en el host está en el run_dir y no quedó nada corriendo; el hub de producción no se tocó.
