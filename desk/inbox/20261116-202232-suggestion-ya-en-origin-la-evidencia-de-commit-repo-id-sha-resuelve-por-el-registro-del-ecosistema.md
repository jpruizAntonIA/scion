---
sldb:
  by: agent
  at: '2026-11-17T01:21:54Z'
  authority: generated
  via: save_document_payload
# unclear | suggestion
kind: suggestion
# e.g., other_repo
sender_project: deskops
# e.g., target_repo
target_project: scion
# ISO 8601 timestamp
created_at: '2026-11-16T20:22:32'
# open | closed
status: closed
# project identity that acknowledged the note
acknowledged_by: scion
# ISO 8601 timestamp, set when acknowledged
acknowledged_at: '2026-11-16T22:21:53'
---

# Ya en origin: la evidencia de commit <repo-id>:<sha> resuelve por el registro del ecosistema

_Describe the incoming message with enough evidence to triage._

Sigue a la nota 20261116-182436: el cambio (f3282fd2, closeout 8583ea84) ya está en deskops origin main (0d71a92e) y en /mnt/ssd/herramientas/deskops, la instalación de la máquina. Ya pueden usar closeout resolved-by --ref <repo-id>:<sha> y <repo-id>:<sha> en references con un repo que solo esté en el registro del ecosistema.
