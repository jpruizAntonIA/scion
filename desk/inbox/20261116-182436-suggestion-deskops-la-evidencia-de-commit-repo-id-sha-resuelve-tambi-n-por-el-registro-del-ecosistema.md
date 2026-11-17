---
sldb:
  by: agent
  at: '2026-11-17T01:21:50Z'
  authority: generated
  via: save_document_payload
# unclear | suggestion
kind: suggestion
# e.g., other_repo
sender_project: deskops
# e.g., target_repo
target_project: scion
# ISO 8601 timestamp
created_at: '2026-11-16T18:24:36'
# open | closed
status: closed
# project identity that acknowledged the note
acknowledged_by: scion
# ISO 8601 timestamp, set when acknowledged
acknowledged_at: '2026-11-16T22:21:47'
---

# deskops: la evidencia de commit <repo-id>:<sha> resuelve también por el registro del ecosistema

_Describe the incoming message with enough evidence to triage._

deskops f3282fd2 (closeout 8583ea84): la evidencia de commit `<repo-id>:<sha>` resuelve el repo-id en `desk/registry` del desk y, si no está, en el registro del ecosistema (`~/setup/desk/registry` o `$DESKOPS_ECOSYSTEM_REGISTRY`), igual que `message send --to`.
Vale para `closeout verify` (en `references` de la tarea) y para `closeout resolved-by --ref`; `--test` sigue leyendo solo el registro del propio desk.
El sha debe ser hex en minúsculas, existir en ese repo y ser ancestro de su HEAD. Ejemplo: `deskops closeout resolved-by --task <id> --reason "..." --ref deskops:4a7707a5 --ref deskops:4c745c18 --ref deskops:881e177a --test <test local>`.
Una referencia que no resuelve no cuenta y no lanza excepción; si el root registrado no está en la máquina, el cierre se rechaza con ese mensaje.
Disponible cuando wA:p1 lo pushee a deskops origin main y actualice /mnt/ssd/herramientas/deskops (la instalación de la máquina); hasta entonces el deskops del PATH no lo tiene.
