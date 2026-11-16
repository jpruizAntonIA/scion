Eres el EJECUTOR deskops-e-c4d00f2df486 (rol deskops-executor, intento 1) del desk de scion. Corres en herdr en robocop2, no en Scion: ignora sciontool; al terminar di "LISTO" en tu última línea.

Tarea: task-hub-de-scion-listener-de-solo-hub-api-para-agentes-en-la-ip-del-bridge-sin-web-ni-dev-auth
Repo y raíz del desk: /mnt/ssd/proyectos/SLDB_1/scion (rama main, código Go). Escribe solo en los files del contrato y en tu run_dir.
run_dir asignado (aquí va agent-api-lab.txt; no inventes otro): /mnt/ssd/proyectos/SLDB_1/scion/runs/subagents/20261116-054630-hub-agent-listener

1. Lee tu rol: runs/subagents/20261116-054630-hub-agent-listener/scion-template/agents.md (/workspace/<repo> = /mnt/ssd/proyectos/SLDB_1/scion; valen Scope, Evidence y When done).
2. Lee el contrato: deskops show task task-hub-de-scion-listener-de-solo-hub-api-para-agentes-en-la-ip-del-bridge-sin-web-ni-dev-auth --root /mnt/ssd/proyectos/SLDB_1/scion. Su goal, scope, implementation_path, validation y done_when mandan.
3. Guarda board.txt, task.txt, next.txt, graph.txt y git-status.txt en el run_dir. No toques run.md.
4. Implementa y corre las validaciones, una a la vez, con TMPDIR=/dev/shm, GOCACHE=/mnt/ssd/cache/go-build y GOMODCACHE=/mnt/ssd/cache/go-mod. Comando exacto y exit code en validation.log. Corre además go test ./cmd completo una vez al final (es el paquete que tocas), con timeout 1500.
5. Escribe result-summary.md: diff (git diff -- cmd/), qué corriste y resultados, la limpieza y qué debe revisar el coordinador.

Respuestas del coordinador a dudas de la revisión (no cambian el contrato):
- El handler es el que hoy arma el modo standalone (la Hub API sin web), con su cadena de middleware (incluido UnifiedAuthMiddleware). El guard de solo agentes va delante.
- Para el test con token de agente, reutiliza el fixture o helper de AgentTokenSvc que ya usan los tests de cmd/ o pkg/hub (búscalo con grep); no inventes uno si existe.
- El texto del error con un solo flag es libre, pero debe nombrar --agent-api-host y --agent-api-port.
- La URL del listener en computeContainerHubEndpoint es http://<ip>:<puerto>.
- Server de lab: HOME=/dev/shm/scion-agentapi-lab/home; lánzalo con server start --foreground ... & y guarda $! en un pidfile del lab; detenlo con kill de ese PID. NUNCA scion server stop: sin PID file sondea 8080/9800, que son de producción.

Prohibido: commitear, pushear, cerrar la tarea, editar desk/ o .sldb/ a mano, git add -A, --autostash, pkill, pgrep, worktrees, sudo, ufw, tocar ~/.scion o el hub de :8080/:9800, relajar los guards existentes de dev-auth o base URL, dejar procesos o archivos en /dev/shm.
Si algo es imposible o ambiguo, no inventes: anótalo en result-summary.md y termina.
