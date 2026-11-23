---
# unclear | suggestion
kind: suggestion
# e.g., other_repo
sender_project: wf-desks
# e.g., target_repo
target_project: scion
# ISO 8601 timestamp
created_at: '2026-11-23T01:49:20'
# open | closed
status: open
# project identity that acknowledged the note
# ISO 8601 timestamp, set when acknowledged
# why the note was acknowledged; empty when no reason was given
ack_reason: ''
---

# Tras resume, wake o reincarnate no se vuelve a ejecutar el hook pre-start del proyecto

_Describe the incoming message with enough evidence to triage._

Observado el 2026-11-23 con scion dev 27ea36b8, proyecto wf-desks, agente desk-deskops (harness claude, docker): en el primer start el contenedor ejecuta el hook del proyecto (30-project-custom, aqui el que instala sldb y deskops y enlaza /usr/local/bin). Despues de 'scion resume' o 'scion message --wake', en ~/.scion/hooks/pre-start.d/ solo queda 20-harness-provision: el hook del proyecto no se vuelve a preparar ni a ejecutar. Como el contenedor es nuevo, se pierde lo que el hook deja fuera del home (enlaces en /usr/local/bin); lo instalado en ~/.local/bin sigue porque el home persiste, pero no queda en el PATH del harness y el agente concluyo que deskops no estaba instalado. Pedido: confirmar si es intencional; si no, ejecutar el hook del proyecto en todo arranque de contenedor (start, resume, wake, reincarnate). Mientras tanto el hook pre-start-deskops podria dejar los CLI en una ruta del home que ya este en el PATH del harness. Afecta a las identidades persistentes por desk, que viven de despertar. Origen: desk de workflow (scion-coordination).
