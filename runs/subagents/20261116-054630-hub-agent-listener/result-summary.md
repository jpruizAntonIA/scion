# result-summary — deskops-e-c4d00f2df486 (ejecutor, intento 1)

Tarea: `task-hub-de-scion-listener-de-solo-hub-api-para-agentes-en-la-ip-del-bridge-sin-web-ni-dev-auth`
Repo: /mnt/ssd/proyectos/SLDB_1/scion, rama main (HEAD 34f2118fe). Nada commiteado ni empujado; la tarea no se cerró; no toqué desk/ ni .sldb/.

## Qué hice

- `cmd/server.go`: flags `--agent-api-host` (default "") y `--agent-api-port` (default 0).
- `cmd/server_agent_api.go` (nuevo):
  - `validateAgentAPIFlags`: van los dos o ninguno. Con uno solo, error de arranque: `--agent-api-host and --agent-api-port must be set together (...)`. También da error con un puerto fuera de 1-65535 y sin hub (`--enable-hub`).
  - `agentAPIGuard`: `/healthz`, `/health` y `/readyz` pasan sin token. Cualquier otro path necesita un token de agente que el `AgentTokenService` del hub valide (`ValidateAgentToken`, la misma comprobación que hace `UnifiedAuthMiddleware`). El token se extrae como en `extractAgentToken`: primero `X-Scion-Agent-Token`, luego `Authorization: Bearer`. Sin token o con uno inválido devuelve 401 JSON antes de llegar al handler, y eso incluye `/api/v1/auth/*`, `scion_dev_*`, `scion_pat_*` y las cookies de sesión. A los requests aceptados les quita `Cookie`, `X-Scion-Issuer-Delegation` y `X-Scion-Federation-Token`; si el token vino en `X-Scion-Agent-Token`, también quita `Authorization`. Así ninguna otra credencial puede autenticar el request aguas abajo. Authz y scopes no cambian (los sigue decidiendo la cadena del hub).
  - `startAgentAPIListener`: hace `net.Listen` síncrono, así que un puerto ocupado o una IP inválida da error de arranque. Luego sirve `agentAPIGuard(hubSrv.Handler())` (el mismo handler `applyMiddleware(mux)` del modo standalone, con `UnifiedAuthMiddleware`) y hace shutdown con `ctx.Done()` (drenaje de hasta 10 s). Sin flags devuelve nil y no abre nada. No sirve la web.
- `cmd/server_foreground.go`: valida los flags antes de revisar puertos y arranca el listener en el paso "12b", después del front propio del hub (Hub API standalone o web) y antes del broker. `errCh` pasa de capacidad 3 a 4 por el nuevo emisor.
- `cmd/server_container_hub.go`: nuevo `containerHubEndpointInputs.AgentAPIEndpoint` = `http://<ip>:<puerto>`. El orden queda: `Configured` > listener de agentes (con el hub en el proceso) > dominio público o IAP > `host.docker.internal`. Sin los flags, el comportamiento es el de antes.
- Tests: `cmd/server_agent_api_test.go` (nuevo) y `TestComputeContainerHubEndpoint_AgentAPIListener` en `cmd/server_container_hub_test.go`.

Los guards `hubAPIStartupPreflight`, `webStartupPreflight` y dev-auth solo en loopback quedan intactos: no se tocaron sus archivos y el listener no pasa por ellos.

## Qué corrí (detalle en validation.log, lab en agent-api-lab.txt)

1. `go test ./cmd -run 'ContainerHubEndpoint|AgentAPI' -count=1`: ok, exit 0.
2. `go vet ./cmd`: limpio, exit 0.
3. Lab en el host con HOME=/dev/shm/scion-agentapi-lab/home y el binario construido del árbol (`go build -buildvcs=false -o /dev/shm/scion-agentapi-lab/scion ./cmd/scion`), web en 127.0.0.1:18080 y listener en 172.17.0.1:18090:
   - `/healthz`=200, `/`=401, `/api/v1/auth/login`=401 y `Bearer scion_dev_x` a `/api/v1/agents`=401.
   - Extra: el dev token real del lab da 401 en 18090 y 200 en la web de loopback.
   - Con un solo flag, exit 1 y un error que nombra los dos flags.
   - Sin flags, 18090 no aparece en `ss -ltn`.
   - El server se detuvo con kill del PID registrado (nunca `scion server stop`).
   - Limpieza: `ls /dev/shm/scion-agentapi-lab` sale con exit 2 y `ss` no lista 18080, 18090 ni 19800.
4. `go test ./cmd -count=1` completo: exit 1 con 4 FAIL, ninguno relacionado con el cambio:
   - `TestDeleteCleanupOnly_PreserveBranch` y `TestExecuteUsageOnError_RunEUsageErrors`: el git del host es 2.43 y se exige ≥ 2.48 (`--relative-paths`).
   - `TestStartHub400OnCreate_NoUsage` y `TestRunSkillsList_TagsReachRequest` (401 "missing authorization header").
   - Los 4 fallan igual en HEAD sin el diff: corrí la suite completa sobre `git archive HEAD` + `git init` en /dev/shm, que ya está borrado. Ese baseline suma 6 FAIL que vienen solo de que `git archive` omite archivos (gcloudignore, Dockerfiles), así que no son comparables.
   - `TestRunSkillsList_TagsReachRequest` pasa aislado tanto con el diff como sin él; depende del orden de la suite y también falla en el baseline completo.

## Qué debe revisar el coordinador

- **Desvío de fixture**: el helper `GenerateAgentToken` de pkg/hub está en `agent_token_testonly_test.go` (paquete `hub`, solo de test), así que no se puede importar desde cmd, y en cmd/ no había un fixture de AgentTokenSvc. El test firma el token con la API exportada que ese helper envuelve: `srv.GetAgentTokenService().SignAgentToken(hub.AgentTokenGrant{...}, "")`, sobre un hub real (`hub.New` + `newTestStore`, el mismo patrón que `newJoinTestHub`).
- **IAP**: con el listener activo, `computeContainerHubEndpoint` devuelve antes de tiempo. No calcula `ColocatedRuntimeHubEndpoints`/`ColocatedPublicHubEndpoint` (la reescritura de una URL pública derivada de IAP) ni consulta la sonda host-gateway. Si en producción se combinan IAP y listener, las reescrituras por runtime no apuntarán al listener. Hoy no aplica en robocop2.
- **Broker no ejercido en el lab**: el broker no arrancó porque el HOME efímero no tiene `image_registry` (degradación de workstation), así que 19800 nunca abrió. Por eso el lab no ejercitó el broker ni el endpoint de contenedor; esa ruta está cubierta por los tests unitarios (`brokerContainerHubConfig` lee los flags). A cambio, el lab no tocó contenedores de producción.
- **Ventana de arranque en standalone**: el listener abre justo después de lanzar la goroutine `hubSrv.Start`, que llama a `StartBackgroundServices` de forma asíncrona. Puede haber una ventana breve antes de que terminen los servicios de fondo. El event publisher ya está cableado en ese punto. En modo combinado abre después de `initWebServer` y `StartBackgroundServices`.
- **Drenaje en el shutdown**: el listener drena con `ctx.Done()` y su propio timeout de 10 s, sin pasar por `shutdownSeq` ni por los hooks `BeforeHTTPDrain` del front. Hay que confirmar que eso basta.
- **Artefacto de la suite**: `go test ./cmd` deja `cmd/telegram_v2.db` en el árbol, porque `extras/scion-telegram/internal/telegram/broker_v2.go` usa `defaultDBPath = "telegram_v2.db"`, relativo al cwd. Es una fuga de test preexistente. Lo borré tras mis corridas; no estaba en el git-status inicial. Vale abrir una tarea aparte.
- Pendiente fuera del alcance: aplicar los flags al hub de producción (:8080), la regla ufw en docker0 y los ejecutores pi en el bridge (tareas hermanas).

## Estado del árbol al terminar (cmd/)

```
 M cmd/server.go
 M cmd/server_container_hub.go
 M cmd/server_container_hub_test.go
 M cmd/server_foreground.go
?? cmd/server_agent_api.go
?? cmd/server_agent_api_test.go
?? cmd/telegram_v2.db
```

## Diff (git diff -- cmd/, archivos versionados)

```diff
diff --git a/cmd/server.go b/cmd/server.go
index ae401d356..4da2327b9 100644
--- a/cmd/server.go
+++ b/cmd/server.go
@@ -248,6 +248,8 @@ func init() {
 	serverStartCmd.Flags().BoolVar(&enableHub, "enable-hub", false, "Enable the Hub API")
 	serverStartCmd.Flags().IntVar(&hubPort, "port", 9810, "Hub API port (standalone mode only; ignored when --enable-web is set, use --web-port instead)")
 	serverStartCmd.Flags().StringVar(&hubHost, "host", "0.0.0.0", "Listen address for the Hub API and web server; the runtime broker listener is set by server.broker.host (workstation default 127.0.0.1; 0.0.0.0 counts as unset)")
+	serverStartCmd.Flags().StringVar(&agentAPIHost, "agent-api-host", "", "Listen address of an extra listener that serves only the Hub API to agents (agent token required; no web, no dev auth), e.g. the docker bridge IP; requires --agent-api-port")
+	serverStartCmd.Flags().IntVar(&agentAPIPort, "agent-api-port", 0, "Port of the agents-only Hub API listener; requires --agent-api-host")
 	serverStartCmd.Flags().StringVar(&dbURL, "db", "", "Database URL/path")
 	serverStartCmd.Flags().BoolVar(&noAutoMigrate, "no-auto-migrate", false, "Skip automatic in-process upgrade of a legacy raw-SQL hub.db to the Ent schema (operator opt-out)")
 
diff --git a/cmd/server_container_hub.go b/cmd/server_container_hub.go
index 07c1417cd..4b548e364 100644
--- a/cmd/server_container_hub.go
+++ b/cmd/server_container_hub.go
@@ -38,6 +38,10 @@ const colocatedHubHostAlias = "scion-hub.internal"
 type containerHubEndpointInputs struct {
 	// Configured is runtime_broker.container_hub_endpoint; when set it wins.
 	Configured string
+	// AgentAPIEndpoint is the agents-only Hub API listener's URL
+	// (agentAPIEndpointURL), or "" when --agent-api-host/--agent-api-port
+	// are not set. It wins over everything but Configured.
+	AgentAPIEndpoint string
 	// HubEnabled reports whether the hub runs in this process (colocated).
 	HubEnabled bool
 	// BrokerHubEndpoint is the broker's own hub URL (localhost when colocated).
@@ -112,6 +116,7 @@ func brokerContainerHubConfig(cfg *config.GlobalConfig, p brokerContainerHubPara
 	in := containerHubEndpointInputs{
 		Configured:              cfg.RuntimeBroker.ContainerHubEndpoint,
 		HubEnabled:              enableHub,
+		AgentAPIEndpoint:        agentAPIEndpointURL(agentAPIHost, agentAPIPort),
 		BrokerHubEndpoint:       p.BrokerHubEndpoint,
 		RuntimeName:             p.RuntimeName,
 		PublicHubEndpoint:       p.PublicHubEndpoint,
@@ -126,6 +131,11 @@ func brokerContainerHubConfig(cfg *config.GlobalConfig, p brokerContainerHubPara
 // computeContainerHubEndpoint decides the hub URL colocated agents are
 // given in place of the broker's own (localhost) hub URL.
 //
+// The order is: runtime_broker.container_hub_endpoint when configured;
+// then the agents-only Hub API listener (--agent-api-host/--agent-api-port)
+// when the hub runs here, which agents on bridge networking reach directly;
+// then the routes below.
+//
 // For colocated Docker agents we prefer bridge networking, so each agent
 // runs in its own network namespace. This avoids the host-global
 // metadata-server (:18380) and telemetry (:4317) port collisions that
@@ -149,6 +159,10 @@ func computeContainerHubEndpoint(in containerHubEndpointInputs, logf func(format
 	if logf == nil {
 		logf = func(string, ...any) {}
 	}
+	if in.Configured == "" && in.HubEnabled && in.AgentAPIEndpoint != "" {
+		logf("Colocated agents routed via the agent API listener %s", in.AgentAPIEndpoint)
+		return containerHubEndpointResult{Endpoint: in.AgentAPIEndpoint, HubListenPort: in.HubListenPort}
+	}
 	if in.Configured != "" || !in.HubEnabled || in.BrokerHubEndpoint == "" || in.RuntimeName == "" {
 		return containerHubEndpointResult{Endpoint: in.Configured, HubListenPort: in.HubListenPort}
 	}
diff --git a/cmd/server_container_hub_test.go b/cmd/server_container_hub_test.go
index c8d2a778f..b222a62f3 100644
--- a/cmd/server_container_hub_test.go
+++ b/cmd/server_container_hub_test.go
@@ -657,3 +657,62 @@ func TestComputeContainerHubEndpointHostGatewayLogLevel(t *testing.T) {
 		})
 	}
 }
+
+func TestComputeContainerHubEndpoint_AgentAPIListener(t *testing.T) {
+	base := containerHubEndpointInputs{
+		HubEnabled:        true,
+		BrokerHubEndpoint: "http://localhost:8080",
+		RuntimeName:       "docker",
+		HubListenPort:     8080,
+	}
+	probeCalled := false
+	noGateway := func() bool { probeCalled = true; return false }
+
+	t.Run("listener wins over host.docker.internal", func(t *testing.T) {
+		in := base
+		in.AgentAPIEndpoint = "http://172.17.0.1:18090"
+		got := computeContainerHubEndpoint(in, nil)
+		assert.Equal(t, containerHubEndpointResult{Endpoint: "http://172.17.0.1:18090", HubListenPort: 8080}, got)
+	})
+	t.Run("listener wins over a public domain and IAP", func(t *testing.T) {
+		for _, src := range []hubEndpointSource{hubEndpointSourceIAPAudience, hubEndpointSourceConfig} {
+			in := base
+			in.AgentAPIEndpoint = "http://172.17.0.1:18090"
+			in.PublicHubEndpoint = "https://scion.example.com"
+			in.PublicHubEndpointSource = src
+			in.HostGatewaySupported = noGateway
+			got := computeContainerHubEndpoint(in, nil)
+			assert.Equal(t, "http://172.17.0.1:18090", got.Endpoint)
+			assert.Empty(t, got.ColocatedRuntimeHubEndpoints)
+		}
+		assert.False(t, probeCalled, "host-gateway probe is not needed with the listener")
+	})
+	t.Run("configured wins over the listener", func(t *testing.T) {
+		in := base
+		in.AgentAPIEndpoint = "http://172.17.0.1:18090"
+		in.Configured = "http://hub.example:9999"
+		got := computeContainerHubEndpoint(in, nil)
+		assert.Equal(t, "http://hub.example:9999", got.Endpoint)
+	})
+	t.Run("without the listener nothing changes", func(t *testing.T) {
+		got := computeContainerHubEndpoint(base, nil)
+		assert.Equal(t, "http://host.docker.internal:8080", got.Endpoint)
+	})
+	t.Run("brokerContainerHubConfig reads the flags", func(t *testing.T) {
+		oldHost, oldPort, oldHub := agentAPIHost, agentAPIPort, enableHub
+		t.Cleanup(func() { agentAPIHost, agentAPIPort, enableHub = oldHost, oldPort, oldHub })
+		agentAPIHost, agentAPIPort, enableHub = "172.17.0.1", 18090, true
+		got := brokerContainerHubConfig(&config.GlobalConfig{}, brokerContainerHubParams{
+			RuntimeName:       "docker",
+			BrokerHubEndpoint: "http://localhost:8080",
+		}, nil)
+		assert.Equal(t, "http://172.17.0.1:18090", got.Endpoint)
+
+		agentAPIHost, agentAPIPort = "", 0
+		got = brokerContainerHubConfig(&config.GlobalConfig{}, brokerContainerHubParams{
+			RuntimeName:       "docker",
+			BrokerHubEndpoint: "http://localhost:8080",
+		}, nil)
+		assert.NotEqual(t, "http://172.17.0.1:18090", got.Endpoint)
+	})
+}
diff --git a/cmd/server_foreground.go b/cmd/server_foreground.go
index 2106b4067..cb297869d 100644
--- a/cmd/server_foreground.go
+++ b/cmd/server_foreground.go
@@ -331,6 +331,11 @@ func runServerStart(cmd *cobra.Command, args []string) error {
 		return err
 	}
 
+	// The agents-only Hub API listener: both flags or neither.
+	if err := validateAgentAPIFlags(agentAPIHost, agentAPIPort, enableHub); err != nil {
+		return err
+	}
+
 	// 6. Check ports
 	if err := checkServerPorts(cfg); err != nil {
 		return err
@@ -394,7 +399,7 @@ func runServerStart(cmd *cobra.Command, args []string) error {
 	}
 
 	var wg sync.WaitGroup
-	errCh := make(chan error, 3)
+	errCh := make(chan error, 4)
 
 	// Server boot hook: warn about legacy environment variables scion no
 	// longer reads, before project discovery and storage init. This is the
@@ -724,6 +729,17 @@ func runServerStart(cmd *cobra.Command, args []string) error {
 		}()
 	}
 
+	// 12b. The agents-only Hub API listener (--agent-api-host/
+	// --agent-api-port): the same Hub API handler as standalone mode,
+	// behind agentAPIGuard. It opens after the hub's own front (standalone
+	// Hub API or web), once the hub's background services and event
+	// publisher are wired, and before the broker registers.
+	if enableHub && hubSrv != nil {
+		if _, err := startAgentAPIListener(ctx, agentAPIHost, agentAPIPort, hubSrv.Handler(), hubAgentTokenValidator(hubSrv.GetAgentTokenService()), &wg, errCh); err != nil {
+			return err
+		}
+	}
+
 	// 13. Start Broker
 	// On a Cloud Run service host, warn once that async launches need CPU
 	// allocated outside requests (ptone/scion#4763). No-op elsewhere.
```

## Archivos nuevos (sin versionar): cmd/server_agent_api.go, cmd/server_agent_api_test.go

### cmd/server_agent_api.go
```go
// Copyright 2026 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package cmd

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log/slog"
	"net"
	"net/http"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/GoogleCloudPlatform/scion/pkg/hub"
)

// The agent API listener (--agent-api-host/--agent-api-port) is an extra
// HTTP listener that serves only the Hub API, and only to agents: it lets
// bridge-networked agent containers reach a hub whose web frontend and dev
// auth stay on loopback. It never serves the web frontend, and every
// request except the health checks must carry a valid agent token; dev,
// personal access, session and OAuth credentials are refused there, so the
// loopback-only guards on dev auth and the web base URL
// (hubAPIStartupPreflight, webStartupPreflight) do not apply to it.

var (
	// agentAPIHost is --agent-api-host.
	agentAPIHost string
	// agentAPIPort is --agent-api-port.
	agentAPIPort int
)

// agentAPIHeaderToken is the header agents send their token in
// (pkg/hub extractAgentToken checks it before the Authorization bearer).
const agentAPIHeaderToken = "X-Scion-Agent-Token"

// agentAPIStrippedHeaders carry non-agent credentials. The guard removes
// them before the Hub API handler sees the request, so only the agent token
// the guard validated can authenticate it.
var agentAPIStrippedHeaders = []string{
	"Cookie",                    // web sessions
	"X-Scion-Issuer-Delegation", // workload issuer delegation
	"X-Scion-Federation-Token",  // federation OIDC
}

// agentAPIShutdownTimeout bounds the agent API listener's HTTP drain.
const agentAPIShutdownTimeout = 10 * time.Second

// validateAgentAPIFlags checks that --agent-api-host and --agent-api-port
// are set together, and that the listener has a hub to serve.
func validateAgentAPIFlags(host string, port int, hubEnabled bool) error {
	host = strings.TrimSpace(host)
	if host == "" && port == 0 {
		return nil
	}
	if host == "" || port == 0 {
		return fmt.Errorf("--agent-api-host and --agent-api-port must be set together (got --agent-api-host=%q --agent-api-port=%d)", host, port)
	}
	if port < 1 || port > 65535 {
		return fmt.Errorf("--agent-api-port %d is out of range (1-65535)", port)
	}
	if !hubEnabled {
		return fmt.Errorf("--agent-api-host and --agent-api-port require the hub (--enable-hub)")
	}
	return nil
}

// agentAPIConfigured reports whether both agent API flags are set.
func agentAPIConfigured(host string, port int) bool {
	return strings.TrimSpace(host) != "" && port > 0
}

// agentAPIEndpointURL is the URL agents reach the agent API listener at,
// http://<host>:<port>, or "" when the listener is not configured.
func agentAPIEndpointURL(host string, port int) string {
	if !agentAPIConfigured(host, port) {
		return ""
	}
	return "http://" + net.JoinHostPort(strings.TrimSpace(host), strconv.Itoa(port))
}

// agentTokenValidator validates an agent token: nil when the token is a
// valid agent token (see hubAgentTokenValidator).
type agentTokenValidator func(token string) error

// hubAgentTokenValidator validates tokens with the hub's agent token
// service, the same check UnifiedAuthMiddleware makes. A nil service gives
// a nil validator, which refuses every token.
func hubAgentTokenValidator(svc *hub.AgentTokenService) agentTokenValidator {
	if svc == nil {
		return nil
	}
	return func(token string) error {
		_, err := svc.ValidateAgentToken(token)
		return err
	}
}

// isAgentAPIHealthPath reports whether path is a health check, served on
// the agent API listener without a token (the paths pkg/hub
// isHealthEndpoint lets through unauthenticated).
func isAgentAPIHealthPath(path string) bool {
	return path == "/healthz" || path == "/health" || path == "/readyz"
}

// agentAPIRequestToken returns the agent token of r the way pkg/hub
// extractAgentToken finds it (X-Scion-Agent-Token first, then an
// Authorization bearer), and whether it came from X-Scion-Agent-Token.
func agentAPIRequestToken(r *http.Request) (token string, fromHeader bool) {
	if t := r.Header.Get(agentAPIHeaderToken); t != "" {
		return t, true
	}
	scheme, rest, ok := strings.Cut(r.Header.Get("Authorization"), " ")
	if !ok || !strings.EqualFold(scheme, "bearer") {
		return "", false
	}
	return rest, false
}

// agentAPIGuard wraps the Hub API handler for the agent API listener:
// health checks pass without a token; every other request needs an agent
// token that validator accepts, or it gets 401 before reaching next. Dev
// tokens (scion_dev_*), personal access tokens (scion_pat_*), web sessions
// and the /api/v1/auth/* endpoints are therefore refused. What a valid
// agent may do is still decided by next (UnifiedAuthMiddleware and authz,
// from the token's scopes). A nil validator refuses every token.
func agentAPIGuard(next http.Handler, validator agentTokenValidator) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if isAgentAPIHealthPath(r.URL.Path) {
			next.ServeHTTP(w, r)
			return
		}
		token, fromHeader := agentAPIRequestToken(r)
		if token == "" {
			writeAgentAPIUnauthorized(w, "agent token required on the agent API listener")
			return
		}
		if validator == nil || validator(token) != nil {
			writeAgentAPIUnauthorized(w, "invalid agent token")
			return
		}
		r = r.Clone(r.Context())
		for _, h := range agentAPIStrippedHeaders {
			r.Header.Del(h)
		}
		if fromHeader {
			// The validated token is in X-Scion-Agent-Token; drop any other
			// bearer so it cannot authenticate the request instead.
			r.Header.Del("Authorization")
		}
		next.ServeHTTP(w, r)
	})
}

// writeAgentAPIUnauthorized writes the guard's 401 in the Hub API error shape.
func writeAgentAPIUnauthorized(w http.ResponseWriter, msg string) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("WWW-Authenticate", `Bearer realm="scion-agent-api"`)
	w.WriteHeader(http.StatusUnauthorized)
	_ = json.NewEncoder(w).Encode(map[string]any{
		"error": map[string]any{"code": "unauthorized", "message": msg},
	})
}

// agentAPIListener is a running agent API listener.
type agentAPIListener struct {
	srv  *http.Server
	ln   net.Listener
	once sync.Once
	err  error
}

// Addr is the listener's bound address.
func (l *agentAPIListener) Addr() net.Addr { return l.ln.Addr() }

// Shutdown drains the listener; it is safe to call more than once.
func (l *agentAPIListener) Shutdown(ctx context.Context) error {
	l.once.Do(func() { l.err = l.srv.Shutdown(ctx) })
	return l.err
}

// startAgentAPIListener opens the agent API listener on host:port with
// hubHandler (the Hub API handler, as served in standalone mode) behind
// agentAPIGuard. It returns nil, nil when the listener is not configured.
// The bind happens before it returns, so a busy or invalid address is a
// startup error; serve errors go to errCh. The listener shuts down when
// ctx is done, and wg is done when it has.
func startAgentAPIListener(ctx context.Context, host string, port int, hubHandler http.Handler, validator agentTokenValidator, wg *sync.WaitGroup, errCh chan<- error) (*agentAPIListener, error) {
	if !agentAPIConfigured(host, port) {
		return nil, nil
	}
	addr := net.JoinHostPort(strings.TrimSpace(host), strconv.Itoa(port))
	ln, err := net.Listen("tcp", addr)
	if err != nil {
		return nil, fmt.Errorf("agent API listener on %s: %w", addr, err)
	}
	l := &agentAPIListener{
		srv: &http.Server{
			Handler:           agentAPIGuard(hubHandler, validator),
			ReadHeaderTimeout: 30 * time.Second,
		},
		ln: ln,
	}
	slog.Info("Agent API listener started (Hub API for agents only, no web, no dev auth)", "addr", ln.Addr().String())
	wg.Add(2)
	go func() {
		defer wg.Done()
		if err := l.srv.Serve(ln); err != nil && !errors.Is(err, http.ErrServerClosed) {
			errCh <- fmt.Errorf("agent API listener error: %w", err)
		}
	}()
	go func() {
		defer wg.Done()
		<-ctx.Done()
		sctx, cancel := context.WithTimeout(context.Background(), agentAPIShutdownTimeout)
		defer cancel()
		_ = l.Shutdown(sctx)
	}()
	return l, nil
}
```
### cmd/server_agent_api_test.go
```go
// Copyright 2026 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package cmd

import (
	"context"
	"fmt"
	"net"
	"net/http"
	"net/http/httptest"
	"strings"
	"sync"
	"testing"
	"time"

	"github.com/GoogleCloudPlatform/scion/pkg/hub"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const agentAPITestDevToken = "scion_dev_agentapi_test"

// newAgentAPITestHub is a hub with dev auth on, so a dev token is accepted
// by the plain Hub API handler, and an agent token signed by the hub's own
// agent token service (the one UnifiedAuthMiddleware validates against).
func newAgentAPITestHub(t *testing.T) (srv *hub.Server, agentToken string) {
	t.Helper()
	cfg := hub.DefaultServerConfig()
	cfg.DevAuthToken = agentAPITestDevToken
	cfg.DisableCloudLogQuery = true
	cfg.DevUserConfig = hub.DevUserConfig{Username: "dev", DisplayName: "Development User", Email: "dev@localhost"}
	srv, err := hub.New(cfg, newTestStore(t))
	require.NoError(t, err)
	t.Cleanup(func() { _ = srv.Shutdown(context.Background()) })
	svc := srv.GetAgentTokenService()
	require.NotNil(t, svc)
	agentToken, _, err = svc.SignAgentToken(hub.AgentTokenGrant{
		AgentID:   uuid.NewString(),
		ProjectID: uuid.NewString(),
		Scopes:    []hub.AgentTokenScope{hub.ScopeProjectRead},
	}, "")
	require.NoError(t, err)
	return srv, agentToken
}

func agentAPIGet(t *testing.T, base, path string, headers map[string]string) int {
	t.Helper()
	req, err := http.NewRequest(http.MethodGet, base+path, nil)
	require.NoError(t, err)
	for k, v := range headers {
		req.Header.Set(k, v)
	}
	resp, err := http.DefaultClient.Do(req)
	require.NoError(t, err)
	_ = resp.Body.Close()
	return resp.StatusCode
}

func TestAgentAPIGuard_OnlyAgentsReachTheHubAPI(t *testing.T) {
	srv, agentToken := newAgentAPITestHub(t)

	// Baseline: the plain Hub API handler accepts the dev token, so the
	// 401s below come from the guard.
	plain := httptest.NewServer(srv.Handler())
	t.Cleanup(plain.Close)
	require.Equal(t, http.StatusOK, agentAPIGet(t, plain.URL, "/api/v1/agents", map[string]string{"Authorization": "Bearer " + agentAPITestDevToken}))

	guarded := httptest.NewServer(agentAPIGuard(srv.Handler(), hubAgentTokenValidator(srv.GetAgentTokenService())))
	t.Cleanup(guarded.Close)

	tests := []struct {
		name    string
		path    string
		headers map[string]string
		want    int
	}{
		{"healthz without token", "/healthz", nil, http.StatusOK},
		{"readyz without token", "/readyz", nil, http.StatusOK},
		{"no token", "/api/v1/agents", nil, http.StatusUnauthorized},
		{"root without token (no web)", "/", nil, http.StatusUnauthorized},
		{"auth login without token", "/api/v1/auth/login", nil, http.StatusUnauthorized},
		{"auth providers without token", "/api/v1/auth/providers", nil, http.StatusUnauthorized},
		{"bearer scion_dev_x", "/api/v1/agents", map[string]string{"Authorization": "Bearer scion_dev_x"}, http.StatusUnauthorized},
		{"bearer real dev token", "/api/v1/agents", map[string]string{"Authorization": "Bearer " + agentAPITestDevToken}, http.StatusUnauthorized},
		{"bearer scion_pat", "/api/v1/agents", map[string]string{"Authorization": "Bearer scion_pat_abc"}, http.StatusUnauthorized},
		{"session cookie only", "/api/v1/agents", map[string]string{"Cookie": "scion_session=abc"}, http.StatusUnauthorized},
		{"invalid agent header", "/api/v1/agents", map[string]string{"X-Scion-Agent-Token": "not-a-jwt"}, http.StatusUnauthorized},
		{"valid agent header", "/api/v1/agents", map[string]string{"X-Scion-Agent-Token": agentToken}, http.StatusOK},
		{"valid agent bearer", "/api/v1/agents", map[string]string{"Authorization": "Bearer " + agentToken}, http.StatusOK},
		{"valid agent header with a dev bearer", "/api/v1/agents", map[string]string{"X-Scion-Agent-Token": agentToken, "Authorization": "Bearer " + agentAPITestDevToken}, http.StatusOK},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.Equal(t, tt.want, agentAPIGet(t, guarded.URL, tt.path, tt.headers))
		})
	}
	// /health is passed through without a token (the hub's own answer,
	// whatever it is, never the guard's 401).
	assert.NotEqual(t, http.StatusUnauthorized, agentAPIGet(t, guarded.URL, "/health", nil))
}

func TestAgentAPIGuard_StripsOtherCredentials(t *testing.T) {
	var seen http.Header
	next := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		seen = r.Header.Clone()
	})
	ok := agentTokenValidator(func(string) error { return nil })
	h := agentAPIGuard(next, ok)

	req := httptest.NewRequest(http.MethodGet, "/api/v1/agents", nil)
	req.Header.Set("X-Scion-Agent-Token", "agent-jwt")
	req.Header.Set("Authorization", "Bearer scion_dev_x")
	req.Header.Set("Cookie", "scion_session=abc")
	req.Header.Set("X-Scion-Issuer-Delegation", "d")
	req.Header.Set("X-Scion-Federation-Token", "f")
	h.ServeHTTP(httptest.NewRecorder(), req)
	require.NotNil(t, seen)
	assert.Equal(t, "agent-jwt", seen.Get("X-Scion-Agent-Token"))
	for _, k := range []string{"Authorization", "Cookie", "X-Scion-Issuer-Delegation", "X-Scion-Federation-Token"} {
		assert.Empty(t, seen.Get(k), k)
	}

	// An agent JWT as bearer stays the request's credential.
	seen = nil
	req = httptest.NewRequest(http.MethodGet, "/api/v1/agents", nil)
	req.Header.Set("Authorization", "Bearer agent-jwt")
	h.ServeHTTP(httptest.NewRecorder(), req)
	require.NotNil(t, seen)
	assert.Equal(t, "Bearer agent-jwt", seen.Get("Authorization"))
}

func TestAgentAPIGuard_NilValidatorRefusesTokens(t *testing.T) {
	h := agentAPIGuard(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {}), nil)
	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/agents", nil)
	req.Header.Set("X-Scion-Agent-Token", "anything")
	h.ServeHTTP(rr, req)
	assert.Equal(t, http.StatusUnauthorized, rr.Code)
	rr = httptest.NewRecorder()
	h.ServeHTTP(rr, httptest.NewRequest(http.MethodGet, "/readyz", nil))
	assert.Equal(t, http.StatusOK, rr.Code)
}

func TestAgentAPIFlags_MustBeSetTogether(t *testing.T) {
	assert.NoError(t, validateAgentAPIFlags("", 0, true))
	assert.NoError(t, validateAgentAPIFlags("", 0, false))
	assert.NoError(t, validateAgentAPIFlags("172.17.0.1", 18090, true))
	for _, tc := range []struct {
		host string
		port int
	}{{"172.17.0.1", 0}, {"", 18090}, {"  ", 18090}} {
		err := validateAgentAPIFlags(tc.host, tc.port, true)
		require.Error(t, err, "%q %d", tc.host, tc.port)
		assert.Contains(t, err.Error(), "--agent-api-host")
		assert.Contains(t, err.Error(), "--agent-api-port")
	}
	assert.Error(t, validateAgentAPIFlags("172.17.0.1", 70000, true))
	assert.Error(t, validateAgentAPIFlags("172.17.0.1", -1, true))
	err := validateAgentAPIFlags("172.17.0.1", 18090, false)
	require.Error(t, err)
	assert.Contains(t, err.Error(), "--enable-hub")
}

func TestAgentAPIFlags_Registered(t *testing.T) {
	for _, name := range []string{"agent-api-host", "agent-api-port"} {
		f := serverStartCmd.Flags().Lookup(name)
		require.NotNil(t, f, name)
	}
	assert.Equal(t, "", serverStartCmd.Flags().Lookup("agent-api-host").DefValue)
	assert.Equal(t, "0", serverStartCmd.Flags().Lookup("agent-api-port").DefValue)
}

func TestAgentAPIEndpointURL(t *testing.T) {
	assert.Equal(t, "http://172.17.0.1:18090", agentAPIEndpointURL("172.17.0.1", 18090))
	assert.Equal(t, "", agentAPIEndpointURL("", 18090))
	assert.Equal(t, "", agentAPIEndpointURL("172.17.0.1", 0))
}

func TestAgentAPIListener_NotOpenedWithoutFlags(t *testing.T) {
	var wg sync.WaitGroup
	errCh := make(chan error, 1)
	l, err := startAgentAPIListener(context.Background(), "", 0, http.NotFoundHandler(), nil, &wg, errCh)
	require.NoError(t, err)
	assert.Nil(t, l)
	wg.Wait()
}

// freeLoopbackPort returns a currently free 127.0.0.1 port.
func freeLoopbackPort(t *testing.T) int {
	t.Helper()
	ln, err := net.Listen("tcp", "127.0.0.1:0")
	require.NoError(t, err)
	port := ln.Addr().(*net.TCPAddr).Port
	require.NoError(t, ln.Close())
	return port
}

func TestAgentAPIListener_ServesHubAPIToAgentsOnly(t *testing.T) {
	srv, agentToken := newAgentAPITestHub(t)
	ctx, cancel := context.WithCancel(context.Background())
	var wg sync.WaitGroup
	errCh := make(chan error, 1)
	port := freeLoopbackPort(t)
	l, err := startAgentAPIListener(ctx, "127.0.0.1", port, srv.Handler(), hubAgentTokenValidator(srv.GetAgentTokenService()), &wg, errCh)
	require.NoError(t, err)
	require.NotNil(t, l)
	base := fmt.Sprintf("http://127.0.0.1:%d", port)

	assert.Equal(t, http.StatusOK, agentAPIGet(t, base, "/healthz", nil))
	assert.Equal(t, http.StatusUnauthorized, agentAPIGet(t, base, "/", nil))
	assert.Equal(t, http.StatusUnauthorized, agentAPIGet(t, base, "/api/v1/auth/login", nil))
	assert.Equal(t, http.StatusUnauthorized, agentAPIGet(t, base, "/api/v1/agents", map[string]string{"Authorization": "Bearer " + agentAPITestDevToken}))
	assert.Equal(t, http.StatusOK, agentAPIGet(t, base, "/api/v1/agents", map[string]string{"X-Scion-Agent-Token": agentToken}))

	// A second listener on the same address is a startup error.
	_, err = startAgentAPIListener(ctx, "127.0.0.1", port, srv.Handler(), nil, &wg, errCh)
	require.Error(t, err)
	assert.True(t, strings.Contains(err.Error(), "agent API listener"), err.Error())

	cancel()
	done := make(chan struct{})
	go func() { wg.Wait(); close(done) }()
	select {
	case <-done:
	case <-time.After(15 * time.Second):
		t.Fatal("agent API listener did not shut down")
	}
	select {
	case err := <-errCh:
		t.Fatalf("unexpected serve error: %v", err)
	default:
	}
	_, err = net.DialTimeout("tcp", fmt.Sprintf("127.0.0.1:%d", port), time.Second)
	assert.Error(t, err, "listener still accepting after shutdown")
}
```
