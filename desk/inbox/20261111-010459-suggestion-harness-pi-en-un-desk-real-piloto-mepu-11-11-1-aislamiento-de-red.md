---
# unclear | suggestion
kind: suggestion
# e.g., other_repo
sender_project: scion
# e.g., target_repo
target_project: scion
# ISO 8601 timestamp
created_at: '2026-11-11T01:04:59'
# open | closed
status: open
# project identity that acknowledged the note
# ISO 8601 timestamp, set when acknowledged
---

# Harness pi en un desk real (piloto mepu, 11-11): (1) aislamiento de red:

_Describe the incoming message with enough evidence to triage._

Harness pi en un desk real (piloto mepu, 11-11): (1) aislamiento de red: con el Hub en loopback los ejecutores van con --network=host y alcanzan los Postgres locales con datos reales; hace falta un endpoint del Hub no loopback (sin SCION_FORCE_HOST_NETWORK) y un test desde dentro del contenedor que muestre que 127.0.0.1:15432 no responde (ojo: descarga-adjuntos escucha en 0.0.0.0:8000); (2) la imagen scion-pi-fork no trae pytest, dagster ni spec2viz, y el ejecutor armó un venv en /tmp; (3) el worktree de tarea no trae .sldb (store gitignored en mepu) y make codigo-doc no corre dentro. Detalle en ~/.claude memoria de mepu y en heyantonia/mepu#246.
