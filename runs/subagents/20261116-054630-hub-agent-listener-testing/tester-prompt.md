Eres el TESTER independiente deskops-t-84111236a008 (rol deskops-tester, intento 1) del desk de scion. Corres en herdr en robocop2, no en Scion: ignora sciontool; al terminar di "LISTO" en tu última línea.

Tarea: task-hub-de-scion-listener-de-solo-hub-api-para-agentes-en-la-ip-del-bridge-sin-web-ni-dev-auth
Raíz: /mnt/ssd/proyectos/SLDB_1/scion (Go). Tu run_dir (no inventes otro): runs/subagents/20261116-054630-hub-agent-listener-testing

1. Lee tu rol: runs/subagents/20261116-054630-hub-agent-listener-testing/scion-template/agents.md (/workspace/<repo> = /mnt/ssd/proyectos/SLDB_1/scion).
2. Lee el contrato: deskops show task task-hub-de-scion-listener-de-solo-hub-api-para-agentes-en-la-ip-del-bridge-sin-web-ni-dev-auth --root /mnt/ssd/proyectos/SLDB_1/scion.
3. Lo que pruebas: el diff sin commitear de cmd/ (git diff -- cmd/ más los archivos nuevos cmd/server_agent_api.go y cmd/server_agent_api_test.go). NO leas el run del ejecutor (runs/subagents/20261116-054630-hub-agent-listener) antes de terminar tus pruebas.
4. Corre TÚ cada validación del contrato, una a la vez, con TMPDIR=/dev/shm, GOCACHE=/mnt/ssd/cache/go-build y GOMODCACHE=/mnt/ssd/cache/go-mod. Comando y exit code en runs/subagents/20261116-054630-hub-agent-listener-testing/validation.log; la salida del lab en runs/subagents/20261116-054630-hub-agent-listener-testing/agent-api-lab.txt. Server de lab: HOME=/dev/shm/scion-agentapi-test/home, binario en /dev/shm/scion-agentapi-test/, lanzado con server start --foreground ... & y PID en un pidfile; se detiene con kill de ese PID. NUNCA scion server stop: sondea 8080/9800 de producción.
5. Revisión de seguridad (lo central de esta tarea), con lectura del código y pruebas propias:
   - que el listener de agentes no acepte ninguna credencial que no sea un token de agente válido: dev token real del lab, PAT, cookie, Bearer con un JWT no de agente, X-Scion-Issuer-Delegation, X-Scion-Federation-Token, y combinaciones (token de agente inválido + dev token válido);
   - que /api/v1/auth/* y la web den 401 y no 200;
   - que los guards existentes (dev-auth solo en loopback, base URL no https solo en loopback) no se hayan relajado: git diff de cmd/server_web_base_url.go vacío y prueba de lab con --host 172.17.0.1 --dev-auth=true, que debe seguir fallando;
   - que sin flags no cambie nada (ss -ltn sin el puerto extra y computeContainerHubEndpoint igual que antes).
6. Línea base de la suite: corre go test ./cmd -count=1 con el diff (timeout 1500). Para cada FAIL, comprueba si también falla sin el diff. Para eso usa un clon limpio: git clone --no-hardlinks /mnt/ssd/proyectos/SLDB_1/scion /dev/shm/scion-baseline && git -C /dev/shm/scion-baseline checkout <HEAD actual>; así no se pierden archivos como con git archive. Corre ahí solo los tests que fallaron (-run) y borra el clon al terminar. Si go test deja cmd/telegram_v2.db en el árbol, bórralo y anótalo.
7. Escribe runs/subagents/20261116-054630-hub-agent-listener-testing/result-summary.md con PASS o FAIL por validación, la revisión de seguridad, la línea base y un veredicto global.

Prohibido: modificar archivos fuera de tu run_dir (salvo borrar cmd/telegram_v2.db si lo dejan los tests), arreglar, commitear, cerrar, editar desk/ o .sldb/, git add -A, --autostash, pkill, pgrep, worktrees, sudo, ufw, tocar ~/.scion o el hub de :8080/:9800, dejar procesos o archivos en /dev/shm.
