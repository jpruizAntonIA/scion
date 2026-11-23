---
# unclear | suggestion
kind: suggestion
# e.g., other_repo
sender_project: wf-desks
# e.g., target_repo
target_project: scion
# ISO 8601 timestamp
created_at: '2026-11-23T01:43:15'
# open | closed
status: open
# project identity that acknowledged the note
# ISO 8601 timestamp, set when acknowledged
# why the note was acknowledged; empty when no reason was given
ack_reason: ''
---

# El hook pre-start-deskops instala sldb y deskops como editables desde SLDB_1: no sirve para desks ajenos

_Describe the incoming message with enough evidence to triage._

scion/hooks/pre-start-deskops.sh exige que el workspace sea la raiz de SLDB_1 y hace 'uv tool install --editable' de sldb y deskops, con lo que el agente necesita esos checkouts montados en escritura. Para despachar agentes de otros desks (primero heyantonia/shared_llm-gateway, pedido de Governance) sin darles escritura sobre SLDB_1 hace falta una variante: instalar desde un paquete o wheel construido en el host, o desde las dos fuentes montadas en solo lectura (instalacion no editable), con la ruta de origen configurable por variable. Hoy el proyecto scion wf-desks lo reusa con un envoltorio (/mnt/ssd/proyectos/wf-desks/bin/pre-start-wf-desks.sh, SCION_WORKSPACE=/mnt/ssd/proyectos/SLDB_1). Relacionado: nota de deskops 20261122-234509 (montaje global de SLDB_1 en todo agente claude) y la tarea runtime-template. Origen: desk de workflow (scion-coordination), 2026-11-23.
