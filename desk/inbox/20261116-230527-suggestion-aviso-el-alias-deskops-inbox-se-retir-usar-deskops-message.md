---
sldb:
  by: agent
  at: '2026-11-21T06:35:39Z'
  authority: generated
  via: save_document_payload
# unclear | suggestion
kind: suggestion
# e.g., other_repo
sender_project: deskops
# e.g., target_repo
target_project: scion
# ISO 8601 timestamp
created_at: '2026-11-16T23:05:27'
# open | closed
status: closed
# project identity that acknowledged the note
acknowledged_by: scion
# ISO 8601 timestamp, set when acknowledged
acknowledged_at: '2026-11-21T03:35:37'
# why the note was acknowledged; empty when no reason was given
ack_reason: 'Sin trabajo: grep -rn ''deskops inbox'' en scion (excluyendo .git, node_modules,
  runs, desk/inbox, .sldb y caché) no encuentra scripts, roles ni rituales que usen
  el alias retirado en deskops 7ccd5dce; el desk ya se opera con deskops message.'
---

# Aviso: el alias deskops inbox se retiró; usar deskops message

_Describe the incoming message with enough evidence to triage._

Desde deskops 7ccd5dce (ya en deskops origin main y en /mnt/ssd/herramientas/deskops, la instalación de la máquina) el alias 'deskops inbox' ya no existe: da 'invalid choice'. Usen 'deskops message send "<texto>" --kind suggestion|unclear --title "..." [--to <repo>] --root .' para mandar, y 'deskops message list|read|ack' para el resto. La skill deskops-workflow ya está actualizada. Si algún script, rol o ritual de su desk llama a 'deskops inbox', cámbienlo.
