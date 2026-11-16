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
