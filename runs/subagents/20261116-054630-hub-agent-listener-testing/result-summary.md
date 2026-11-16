# result-summary — deskops-t-84111236a008 (tester, intento 1)

- Tarea: `task-hub-de-scion-listener-de-solo-hub-api-para-agentes-en-la-ip-del-bridge-sin-web-ni-dev-auth`
- Rol: tester (`role-deskops-tester`), runtime claude en herdr (robocop2). Run: `run-deskops-t-84111236a008`, run_dir `runs/subagents/20261116-054630-hub-agent-listener-testing`.
- Probado: diff sin commitear de `cmd/` sobre HEAD `34f2118fe` (`cmd/server.go`, `cmd/server_container_hub.go`, `cmd/server_container_hub_test.go`, `cmd/server_foreground.go` y los nuevos `cmd/server_agent_api.go` / `cmd/server_agent_api_test.go`).
- No modifiqué nada fuera de mi run_dir, salvo borrar `cmd/telegram_v2.db` (sin trackear) que deja `go test ./cmd`. Nada commiteado, no se cerró la tarea, no toqué desk/, .sldb/, ~/.scion ni el hub de :8080/:9800.
- Evidencia: `validation.log` (comandos y exit codes), `agent-api-lab.txt` (lab), `v1-go-test-filter.txt`, `v2-go-vet.txt`, `suite-cmd-with-diff.txt`, `suite-cmd-with-diff-run2.txt`, `suite-cmd-baseline-failures.txt`, `suite-cmd-baseline-full.txt`, `skills-list-with-diff-isolated.txt`.
- Leí el run del ejecutor solo al terminar mis pruebas. Sus conclusiones coinciden con las mías.

## Validaciones del contrato

| # | Validación | Resultado |
|---|---|---|
| V1 | `go test ./cmd -run 'ContainerHubEndpoint\|AgentAPI' -count=1` | **PASS**: exit 0. Pasan 56 tests/subtests, los nuevos y los ContainerHubEndpoint que ya existían. |
| V2 | `go vet ./cmd` | **PASS**: exit 0, sin salida. |
| V3 | Lab: web en 127.0.0.1:18080 y listener en 172.17.0.1:18090; `/healthz`=200, `/`=401, `/api/v1/auth/login`=401, `Bearer scion_dev_x` a `/api/v1/agents`=401 | **PASS**: los 4 códigos coinciden. |
| V4 | Un solo flag: el server no arranca y el error nombra ambos flags. Sin flags, `ss -ltn` no lista 18090 | **PASS**: probé host sin port y port sin host. Los dos casos dan `Error: --agent-api-host and --agent-api-port must be set together (...)` y el proceso termina. Sin flags arranca, 18090 no escucha y el log no tiene ninguna línea "Agent API listener". |
| V5 | Limpieza: `ls /dev/shm/scion-agentapi-lab` falla y `ss` no lista 18080, 18090 ni 19800 | **PASS**: `ls` de `/dev/shm/scion-agentapi-test` (mi HOME de lab) y de `-lab` da rc=2; `ss` no lista ninguno de los tres puertos. Producción en 127.0.0.1:8080/9800 sigue escuchando y no la toqué. |

Nota del lab: el runtime broker no arranca en el HOME efímero porque no hay `image_registry`, así que 19800 nunca abrió. No afecta al listener.

## Revisión de seguridad (lectura del código + lab con credenciales reales)

Código: `agentAPIGuard` (`cmd/server_agent_api.go`) envuelve el handler entero de la Hub API, así que ninguna ruta queda fuera del guard. Solo deja pasar sin token `/healthz`, `/health` y `/readyz`, comparados por igualdad exacta. Para todo lo demás:
- Extrae el token igual que `pkg/hub/agenttoken.go extractAgentToken`: primero `X-Scion-Agent-Token` y después `Authorization: Bearer`.
- Lo valida con `AgentTokenService.ValidateAgentToken`, que exige HS256 con la clave del hub, `iss=scion-hub` y `aud=scion-hub-api`.
- Con un token aceptado, quita `Cookie`, `X-Scion-Issuer-Delegation` y `X-Scion-Federation-Token`. Si el token vino en el header, quita también `Authorization`.

Con esto, `UnifiedAuthMiddleware` (paso 0 delegación, paso 1 agente) siempre autentica el request como el agente validado. Un validador nil rechaza todo. Authz y scopes siguen intactos aguas abajo.

Lab contra `http://172.17.0.1:18090`. Todo dio **401** salvo los health:

- **dev token REAL del lab**: en Bearer, en `X-Scion-Agent-Token`, en esquema Basic y en `?token=`.
- **PAT REAL**: un `scion_pat_` creado en loopback que da 200 en `/api/v1/auth/me` por 18080. En 18090 da 401 tanto en Bearer como en `X-Scion-Agent-Token`.
- **Cookie de sesión**: sola y combinada con el dev token real.
- **JWT que no son de agente**:
  - iss/aud de usuario;
  - iss/aud de agente firmado con otra clave;
  - `alg=none`.
- **Otras cabeceras de credencial, solas**: `X-Scion-Issuer-Delegation`, `X-Scion-Federation-Token`, `X-Scion-Broker-ID` (HMAC) y `X-Forwarded-User-*`.
- **Combinaciones**:
  - token de agente inválido en el header + dev token real en Bearer;
  - JWT de agente forjado + dev token real;
  - dev token real + federation token.
- **`/api/v1/auth/*`**: `login`, `providers`, `me`, `token`, `cli/device`, `test-login`, `validate` y `tokens` dan 401 sin auth. `POST /api/v1/auth/tokens` y `GET /auth/me` con el dev token real también dan 401.
- **Web**: `/`, `/index.html`, `/login`, `/assets/`, `/auth/login` y `/favicon.ico` dan 401 con JSON `unauthorized`, no HTML. Como control, `/login` en 18080 sí devuelve `text/html` 200.
- **Normalización de ruta**: `/healthz/../api/v1/agents` (`--path-as-is`), `/healthz/x`, `//api/v1/agents` y `/healthz%2f..%2fapi/v1/agents` dan 401.
- **Control en loopback**: el dev token sigue dando 200 en 127.0.0.1:18080.

El camino positivo con un token de agente válido no lo probé en el lab, porque ahí no había agente que lo emitiera. Lo cubre `TestAgentAPIListener_ServesHubAPIToAgentsOnly`: un `hub.Server` real con un token firmado por su `AgentTokenService` da 200 en `/api/v1/agents`, y el dev token da 401 sobre un listener real.

**Guards existentes no relajados**:
- `git diff -- cmd/server_web_base_url.go pkg/` vacío.
- `--host 172.17.0.1 --dev-auth=true` no arranca: "dev auth cannot be enabled when the server is bound to a non-loopback address (172.17.0.1)…". Falla igual sin flags de agentes y con `--agent-api-host/port`.
- `--host 172.17.0.1 --dev-auth=false` no arranca: "refusing to start the web server: its base URL http://localhost:18080 … is not https…".
- En los tres casos ningún puerto quedó abierto.

**Sin flags no cambia nada**:
- `ss -ltn` no lista 18090.
- `computeContainerHubEndpoint` sigue igual: la rama nueva solo entra con `AgentAPIEndpoint != ""`, los tests que ya existían pasan y el subtest "without the listener nothing changes" devuelve `http://host.docker.internal:8080`.

**Veredicto de seguridad: PASS.** No encontré ninguna credencial que no sea de agente y que pase el listener.

## Línea base de la suite `go test ./cmd -count=1` (timeout 1500)

- Con el diff, dos corridas: exit 1, con los mismos 4 FAIL las dos veces.
  - `TestDeleteCleanupOnly_PreserveBranch`
  - `TestExecuteUsageOnError_RunEUsageErrors`
  - `TestRunSkillsList_TagsReachRequest`
  - `TestStartHub400OnCreate_NoUsage`
- Sin el diff, en un clon limpio (`git clone --no-hardlinks` + checkout `34f2118fe` en `/dev/shm/scion-baseline`, ya borrado):
  - Con `-run` de esos 4, fallan 3. `TestRunSkillsList_TagsReachRequest` pasa aislado.
  - Para descartar el diff corrí también la **suite completa** sin el diff, y fallan **los mismos 4**. `TestRunSkillsList_TagsReachRequest` da el mismo `401 missing authorization header`.
  - Aislado y con el diff, ese test pasa 5/5 (`-count=5`). Depende del orden de la suite y es preexistente.
- Causas:
  - Tres de los FAIL vienen del git del host: es 2.43.0 y scion exige ≥ 2.48 (`--relative-paths`).
  - El cuarto, `TestRunSkillsList_TagsReachRequest`, depende del orden de la suite.
  - **Ningún FAIL viene del diff.**
- `go test ./cmd` dejó `cmd/telegram_v2.db` sin trackear tras cada corrida con el diff. Lo borré las dos veces. Es una fuga preexistente: `defaultDBPath` relativo al cwd en extras/scion-telegram.

## Observaciones (no bloquean el contrato)

1. **`/health` en el listener da 404, no 200.** El guard lo deja pasar sin token, pero el handler de la Hub API no tiene `/health`: esa ruta solo existe en el mux web (`pkg/hub/web.go:1366`). En loopback 18080 `/health` da 200. El contrato solo valida `/healthz`, que da 200. Los harnesses que sondeen deberían usar `/healthz` o `/readyz`.
2. **Con el listener activo, todos los runtimes y todas las rutas reciben la URL del bridge.** `computeContainerHubEndpoint` sale antes de calcular `ColocatedRuntimeHubEndpoints` (IAP/público) y no distingue el runtime (docker/podman/k8s), así que a todos les da `http://172.17.0.1:18090`. El orden del contrato lo permite, pero en un broker con podman o k8s, o combinado con IAP, ese endpoint puede no ser alcanzable. El ejecutor también lo señala. Conviene tenerlo presente al aplicarlo en producción.
3. El listener drena en el shutdown con su propio timeout de 10 s, sin pasar por `shutdownSeq` ni por los hooks `BeforeHTTPDrain` (lo señaló el ejecutor). Lo vi en el código y no lo probé aparte. En el lab terminó limpio con SIGTERM.
4. Error de mi primer arranque de lab: el pidfile guardó el PID del subshell y no el del binario. El server real (exe `/dev/shm/scion-agentapi-test/scion`) quedó huérfano hasta que lo identifiqué con `ss -ltnp` y lo detuve con `kill` de ese PID. Después corregí el script (`setsid` sin subshell). Todo está anotado en `agent-api-lab.txt`. No usé pkill, pgrep ni `scion server stop`.
5. Tests que faltan o están viejos: ninguno que bloquee. Los 4 FAIL ambientales o de orden de la suite merecen tareas aparte: git ≥ 2.48 en el host, aislar `TestRunSkillsList_TagsReachRequest` y la fuga de `telegram_v2.db`.

## Veredicto global: **PASS**

V1–V5 pasan. La revisión de seguridad no encuentra ninguna credencial que no sea de agente aceptada por el listener, los guards de dev-auth y de base URL siguen intactos, y sin flags no cambia nada. Los únicos FAIL de la suite también fallan sin el diff. No dejé procesos, archivos en /dev/shm ni puertos de lab abiertos. Lo devuelvo al coordinador para que revise y cierre.
