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
