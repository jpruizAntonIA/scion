---
# unclear | suggestion
kind: suggestion
# e.g., other_repo
sender_project: repo-governance
# e.g., target_repo
target_project: scion
# ISO 8601 timestamp
created_at: '2026-11-20T21:27:19'
# open | closed
status: open
# project identity that acknowledged the note
# ISO 8601 timestamp, set when acknowledged
# why the note was acknowledged; empty when no reason was given
ack_reason: ''
---

# Poner el fork al día con el original y traer extras/herdr-scion

_Describe the incoming message with enough evidence to triage._

El fork está 795 commits atrás de GoogleCloudPlatform/scion y 47 adelante. El original trae desde el 2026-11-09 extras/herdr-scion: un plugin de herdr que muestra los agentes de scion como paneles con su estado (descubrimiento al partir, puente de estado cada 4 s, adjuntarse, partir un agente desde una plantilla, tablero en mosaico, etiqueta scion:<proyecto>/<agente> por panel). JP (20-11) pidió revisar los extras, en particular este. Pedido: fusionar el original, o al menos traer extras/herdr-scion, enlazarlo con herdr plugin link y probarlo contra el hub de robocop 2. El tablero pide herdr 0.9.1; el laptop de JP tiene 0.9.0. Fuente: heyantonia/Governance, rama dev, docs/diagnostico-vsm-2026-11-19/herramientas/h-scion-extras.md.
