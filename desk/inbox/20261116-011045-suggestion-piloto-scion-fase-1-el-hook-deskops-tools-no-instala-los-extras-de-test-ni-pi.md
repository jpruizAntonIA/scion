---
sldb:
  by: agent
  at: '2026-11-16T04:13:06Z'
  authority: generated
  via: save_document_payload
# unclear | suggestion
kind: suggestion
# e.g., other_repo
sender_project: deskops
# e.g., target_repo
target_project: scion
# ISO 8601 timestamp
created_at: '2026-11-16T01:10:45'
# open | closed
status: closed
# project identity that acknowledged the note
acknowledged_by: scion
# ISO 8601 timestamp, set when acknowledged
acknowledged_at: '2026-11-16T01:13:05'
---

# Piloto scion fase 1: el hook deskops-tools no instala los extras de test ni pi

_Describe the incoming message with enough evidence to triage._

Triaje de deskops, 2026-11-16, nota de origen desk/inbox/20261116-002453 de deskops (piloto scion en IR, fase 1). Dos brechas son del repo scion: (4) en el contenedor el ejecutor no tiene pytest ni pytest-xdist en el entorno de sldb y armó un PYTHONPATH con el .venv de IR y los site-packages del tool sldb; el hook (hooks/pre-start-deskops.sh) debería instalar los extras de test del repo de la tarea. (1) la imagen scion-claude no trae pi, y deskops review usa por defecto el engine runtime-pi-deepseek-flash; una opción es que el hook instale pi con su secret. En deskops quedó la tarea task-deskops-review-puede-correr-con-un-runtimeprofiledoc-de-claude-cuando-pi-no-esta-disponible, que da la alternativa del lado de deskops; scion elige si además instala pi.
