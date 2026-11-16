---
sldb:
  by: agent
  at: '2026-11-16T05:14:15Z'
  authority: generated
  via: save_document_payload
# review-<task>-<kind>-<n>
id: review-task-endpoint-no-loopback-del-hub-de-scion-de-producción-para-ejecutores-pi-en-red-bridge-decisión-de-jp-owner-1
# preflight | bundle | reproduction | goldens | owner | node | evidence
kind: owner
# kind evidence only: tests | commit | atom | materialization | document | external
fact: ''
# kind evidence only: what the producer verified, one item per line
value: ''
# doc:<Model>:<id> or empty for reviews of plan nodes
subject: doc:TaskDecisionDoc:task-endpoint-no-loopback-del-hub-de-scion-de-producción-para-ejecutores-pi-en-red-bridge-decisión-de-jp@sha256:49a2cc44b6f4745ce60e3c801634c230cb392c1c0466a7b522ece3c955b22126
# <plan>/dag.yaml#node:<ID>; empty when subject names a document
subject_ref: ''
# RuntimeProfileDoc name or "human"
engine: human
actor: scion
# Run evidence directory under runs/, relative to the project root
run_dir: ''
input_sha256: ''
output_sha256: ''
# pending | accepted | rejected | incomplete
verdict: accepted
reason: 'JP 2026-11-16 delega en el coordinador (vale cualquiera que funcione). Elección:
  (a) agregar --host 172.17.0.1 a los argumentos del hub de producción (~/.scion/server-args.json).
  Por qué: 172.17.0.1 es el gateway de docker0 en robocop2, así que un contenedor
  en red bridge lo alcanza sin --network=host; no se expone en la LAN, a diferencia
  de 0.0.0.0; host.docker.internal resuelve a la misma IP pero exige --add-host en
  cada contenedor. Costos aceptados: el --dev-auth del hub queda visible para cualquier
  contenedor del bridge (máquina de un solo usuario) y los clientes del host apuntan
  a http://172.17.0.1:8080 en vez de localhost. Cómo se aplica: la tarea task-harness-pi-en-desk-real-...
  lo prueba primero en el hub de lab (--host 172.17.0.1 --web-port 18080) y su propuesta-endpoint-hub.md
  trae el comando y la vuelta atrás; el reinicio del hub de :8080 se hace después
  de esa prueba.'
# ISO 8601 timestamp
created_at: '2026-11-16T03:41:09.626276+00:00'
# ISO 8601 timestamp, empty while pending
disposed_at: '2026-11-16T05:14:14.963026+00:00'
disposed_by: scion
# e.g. workspace:desk
tags:
- workspace:desk
---

# Owner review of task-endpoint-no-loopback-del-hub-de-scion-de-producción-para-ejecutores-pi-en-red-bridge-decisión-de-jp

## Summary

_Summarize what was reviewed and the evidence this receipt records._

owner receipt recorded by scion; evidence: (none)

## Disposition

_Record the verdict rationale and who disposed of the review._

Verdict accepted: JP 2026-11-16 delega en el coordinador (vale cualquiera que funcione). Elección: (a) agregar --host 172.17.0.1 a los argumentos del hub de producción (~/.scion/server-args.json). Por qué: 172.17.0.1 es el gateway de docker0 en robocop2, así que un contenedor en red bridge lo alcanza sin --network=host; no se expone en la LAN, a diferencia de 0.0.0.0; host.docker.internal resuelve a la misma IP pero exige --add-host en cada contenedor. Costos aceptados: el --dev-auth del hub queda visible para cualquier contenedor del bridge (máquina de un solo usuario) y los clientes del host apuntan a http://172.17.0.1:8080 en vez de localhost. Cómo se aplica: la tarea task-harness-pi-en-desk-real-... lo prueba primero en el hub de lab (--host 172.17.0.1 --web-port 18080) y su propuesta-endpoint-hub.md trae el comando y la vuelta atrás; el reinicio del hub de :8080 se hace después de esa prueba.
