---
# unclear | suggestion
kind: suggestion
# e.g., other_repo
sender_project: deskops
# e.g., target_repo
target_project: scion
# ISO 8601 timestamp
created_at: '2026-11-22T23:39:12'
# open | closed
status: open
# project identity that acknowledged the note
# ISO 8601 timestamp, set when acknowledged
# why the note was acknowledged; empty when no reason was given
ack_reason: ''
---

# Bloqueante: resume, reincarnate y wake fallan con 'the hub issued no agent token' (falta #1350 en el hub)

_Describe the incoming message with enough evidence to triage._

De: scion-coordination (encargo de JP, workflow scion + deskops; estado en ~/coordinacion/estado-scion-coordination.md). Enviada con la raiz de deskops porque el desk de workflow todavia no esta registrado.

Sintoma (binario instalado, scion dev f6e623c6, hub local con dev-auth, broker co-ubicado, docker): el primer 'scion start' de un agente funciona, pero todo rearranque de un agente que ya existe falla: 'scion resume <agente>', 'scion resume --force', 'scion reincarnate --handoff-file' (y por lo tanto 'message --wake'). El broker responde 500 y el log del server dice 'SCION_AUTH_TOKEN in the start env is not the hub-issued token; dropped' y luego 'agent start refused: the hub issued no agent token'. Reproducido el 2026-11-23 02:28 y 02:33 UTC con desk-a en los proyectos wf-spike y wf-spike-plain; el mismo error esta en el log el 16-11 (ui8-tests) y el 20-11 (ftc-35b).

Causa: en pkg/hub/httpdispatcher.go, DispatchAgentStart (linea ~3692) y DispatchAgentRestart (~3958) tienen 'TODO(#1350): Thread envClassifications to broker via client.StartAgent / RestartAgent' y descartan el mapa ('_ = envClassifications'). El hub si firma el token (beginRun) y lo pone en resolvedEnv con setStartEnvToken, clasificado secret-bootstrap, pero la clasificacion nunca viaja. El broker (pkg/runtimebroker/start_context.go ~641) solo acepta SCION_AUTH_TOKEN del resolvedEnv si viene clasificado EnvKindSecretBootstrap, y pkg/agent/run.go ~1623 rechaza el arranque sin token (commit a30594a04, #4248). El propio TODO avisa: 'fail-closed + nil map = total outage'. El handler del broker ya acepta 'envClassifications' en el cuerpo de start y restart (pkg/runtimebroker/handlers.go ~3467 y ~4763).

Pedido:
1. Pasar envClassifications en client.StartAgent y client.RestartAgent (los cuatro clientes: HTTPRuntimeBrokerClient, AuthenticatedBrokerClient, ControlChannelBrokerClient, HybridBrokerClient; por ejemplo via StartExtras) y borrar los '_ = envClassifications'. O traer el arreglo del original si ya existe, dentro de la puesta al dia del fork (nota jpruizAntonIA/scion#1).
2. Test: start, stop y resume de un agente contra un broker co-ubicado conserva el id y arranca; reincarnate con handoff llega a generation 2 running.
3. Construir el binario sin instalarlo. La instalacion y el reinicio del server los hace scion-coordination en una ventana acordada con el coordinador de SLDB_1 (JP ya autorizo actualizar y reiniciar).

Por que es bloqueante: JP definio la identidad persistente por desk como un agente que se prende y se apaga. Sin resume ni wake no hay piloto.
