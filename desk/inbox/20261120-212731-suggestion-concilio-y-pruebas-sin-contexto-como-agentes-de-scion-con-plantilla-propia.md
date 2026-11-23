---
# unclear | suggestion
kind: suggestion
# e.g., other_repo
sender_project: repo-governance
# e.g., target_repo
target_project: scion
# ISO 8601 timestamp
created_at: '2026-11-20T21:27:31'
# open | closed
status: open
# project identity that acknowledged the note
# ISO 8601 timestamp, set when acknowledged
# why the note was acknowledged; empty when no reason was given
ack_reason: ''
---

# Concilio y pruebas sin contexto como agentes de scion con plantilla propia

_Describe the incoming message with enough evidence to triage._

JP (19-11): el concilio (pi, agy, codex) y las pruebas sin contexto solo existen cuando él los levanta a mano en herdr; deben poder levantarse desde deskops con estado persistente y gobernable en scion. Pedido para este desk: una plantilla por revisor, con identidad y credencial de solo lectura, cada uno con un proveedor distinto, y una plantilla sin memoria para el lector de las pruebas sin contexto. Los topes de turnos, duración y concurrencia los decide scion según el hardware (JP, 20-11). La otra mitad (quién los dispara y dónde queda el informe) se pidió a deskops en jpcosec/deskops#3. Además, extras/scion-a2a-bridge y extras/fs-watcher-tool sirven para hablarle a un agente por un protocolo estándar y para auditar qué archivos tocó cada uno. Fuente: heyantonia/Governance, rama dev, docs/diagnostico-vsm-2026-11-19/herramientas/h-scion-extras.md.
