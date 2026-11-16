# Tester result: task-hub-de-scion-listener-de-solo-hub-api-para-agentes-en-la-ip-del-bridge-sin-web-ni-dev-auth

- Rol: tester (deskops-tester), intento 2. Run: run-deskops-t-84111236a008-a2 (subagente local, no Scion).
- Objeto probado: tests/test_go_hub_agent_api_suite.py (sin commitear) como evidencia de closeout de la implementacion fc771c045, via deskops.testing.foreign_suites.run_foreign_suite.
- HEAD al probar: ver validation.log ([c1]).

## Validaciones

| # | Comando | rc | Resultado |
|---|---------|----|-----------|
| a1 | contrato val. 1: `go test ./cmd -run 'ContainerHubEndpoint\|AgentAPI' -count=1` (GOCACHE/GOMODCACHE/TMPDIR como el contrato) | 0 | PASS (a1-go-test.txt) |
| a2 | contrato val. 2: `go vet ./cmd` | 0 | PASS (a2-go-vet.txt) |
| b | `TMPDIR=/dev/shm uv run --no-project --with pytest --with-editable /mnt/ssd/herramientas/deskops python -m pytest -q -p no:cacheprovider tests/test_go_hub_agent_api_suite.py` | 0 | PASS, 2 passed en 24.67s (b-pytest.txt) |
| c1 | `git merge-base --is-ancestor fc771c045 HEAD` | 0 | PASS |
| c2 | `git diff fc771c045 HEAD -- cmd/server_agent_api.go cmd/server_agent_api_test.go` | 0 | PASS, diff vacio; sin cambios locales en cmd/ |
| d1 | `go test ./cmd -list 'ContainerHubEndpoint\|AgentAPI'` | 0 | PASS, 12 tests (d-go-list.txt) |
| d2 | idem a1 con `-v` | 0 | PASS, 12 `--- PASS`, 0 SKIP, 0 FAIL (d-go-test-v.txt) |

## Revision del test (d)

- Dos tests: `go test ./cmd -run ContainerHubEndpoint|AgentAPI -count=1` y `go vet ./cmd`, pasados como lista de argv a subprocess.run sin shell; el `|` llega literal como regex a -run. Coinciden con las validaciones 1 y 2 del contrato.
- Env: copia de os.environ + setdefault de GOCACHE=/mnt/ssd/cache/go-build, GOMODCACHE=/mnt/ssd/cache/go-mod, TMPDIR=/dev/shm. Observacion menor (no bloqueante): por ser setdefault, si el entorno del llamador ya define esas variables se respetan las del llamador, no las del contrato.
- cwd = raiz del repo (parents[1] de tests/), timeout 900 s; el puente falla con rc!=0, ejecutable ausente o timeout.
- El filtro selecciona 12 tests reales (8 TestAgentAPI*, 4 *ContainerHubEndpoint*), todos se ejecutan y pasan: no es un rc 0 vacio.
- Fuera del alcance del test: validaciones 3-5 del contrato (lab de red en 172.17.0.1, flags parciales, limpieza); su evidencia es la del intento 1 (runs/subagents/20261116-054630-hub-agent-listener-testing), no repetida aqui por instruccion.

## Limpieza

No deje archivos en /dev/shm (pytest-of-robocop/pytest-629 y 630 son de otros procesos). No modifique nada fuera de este run_dir.

## Global: PASS
