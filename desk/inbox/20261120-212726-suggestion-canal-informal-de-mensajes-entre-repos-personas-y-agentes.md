---
# unclear | suggestion
kind: suggestion
# e.g., other_repo
sender_project: repo-governance
# e.g., target_repo
target_project: scion
# ISO 8601 timestamp
created_at: '2026-11-20T21:27:26'
# open | closed
status: open
# project identity that acknowledged the note
# ISO 8601 timestamp, set when acknowledged
# why the note was acknowledged; empty when no reason was given
ack_reason: ''
---

# Canal informal de mensajes entre repos, personas y agentes

_Describe the incoming message with enough evidence to triage._

Decisión 5 de JP (19-11): un canal informal de mensajes entre repos, personas y agentes, aparte de deskops, aprovechando scion. Decisión del 20-11: el agente interno de cada desk lee ese canal y propone tareas o notas de inbox cuando detecta un compromiso; nada de lo que pasa por el canal compromete por sí solo. scion ya tiene un broker de mensajes con plugins: el canal puede ser un plugin de ese broker, con extras/scion-broker-log como punto de partida, en vez de un servicio nuevo sobre el Postgres. Reemplaza la tarea de Governance «canal informal de mensajes entre repos, personas y agentes sobre scion». Fuente: heyantonia/Governance, rama dev, docs/diagnostico-vsm-2026-11-19/herramientas/h-scion-extras.md.
