---
sldb:
  by: agent
  at: '2026-11-16T03:39:20Z'
  authority: generated
  via: save_document_payload
id: task-fase-0-ir-hook-pre-start-deskops-tools-instala-sldb-y-deskops-editables-desde-workspace
status: draft
summary: ''
tags:
- workspace:desk
- artifact:task
current_node: ritual-execution
history: []
references:
- f6e623c69
- 748443c83
depends_on: []
pills: []
files:
- hooks/pre-start-deskops.sh
task_type: task.code
inherits_from: []
inherit_acceptance_context: false
atoms: []
---

# Fase 0 IR: hook pre-start deskops-tools instala sldb y deskops editables desde /workspace

## Rationale

_Explain why this task exists or the business driver behind it._

El hook actual (hooks/pre-start-deskops.sh) instala sldb y deskops desde copias tiradas a /tmp: si una tarea cambia sldb o deskops en el workspace, el agente sigue ejecutando la versión vieja hasta reiniciarse. El brief del piloto scion en IR (fase 0 punto 1) exige modo editable sobre /workspace.

## Goal

_Describe the concrete result this task must produce._

hooks/pre-start-deskops.sh instala sldb y deskops con `uv tool install --editable` directamente desde $SCION_WORKSPACE/sldb y $SCION_WORKSPACE/deskops (por defecto /workspace), con sldb también editable dentro del venv de deskops (`--with-editable`). Un cambio en /workspace/sldb o /workspace/deskops se ve en el siguiente comando del agente sin reinstalar.

## Scope

_State what is in scope and what is out of scope._

IN: hooks/pre-start-deskops.sh (instalación y comentarios). WORKSPACE=${SCION_WORKSPACE:-/workspace} (variable vacía o ausente -> /workspace, expansión de bash ya existente en el script); PYTHON_SPEC=${DESKOPS_PYTHON:-3.13} (ya existente). Se mantiene: uv propio (si no hay uv, se instala con curl o wget; sin ninguno sale con 1), salida 1 si falta $WORKSPACE/sldb/pyproject.toml o $WORKSPACE/deskops/pyproject.toml, y salida 1 si después de instalar no existen los ejecutables sldb y deskops en $HOME/.local/bin; PATH en .profile/.bashrc. Que *.egg-info está ignorado por git en sldb y deskops es un hecho a verificar (git check-ignore), no una acción: no se toca ningún .gitignore. OUT: registrar el hook en el hub ('scion project hook create --name "deskops tools" --script scion/hooks/pre-start-deskops.sh <proyecto>') es un paso de la fase 1 con el hub del fork; imágenes; código de sldb/deskops. Estado: el cambio ya está en main (commit f6e623c69): el ejecutor verifica el hook contra este contrato, no lo reescribe.

## Implementation Path

_Outline the expected implementation route or affected surface._

Reemplazar el bloque de copias (mktemp + tar) por dos `uv tool install --quiet --python $PYTHON_SPEC --reinstall --editable ...`.

## Validation

_List the checks required before this task can close._

- bash -n hooks/pre-start-deskops.sh
- timeout 600 docker run --rm --entrypoint bash --user 1001:1003 -e HOME=/tmp/h -e SCION_WORKSPACE=/workspace -v /mnt/ssd/proyectos/SLDB_1:/workspace -v <scion>/hooks/pre-start-deskops.sh:/hook.sh:ro ghcr.io/jpruizantonia/scion-claude:f6e623c69 -c "mkdir -p /tmp/h && bash /hook.sh && cd /tmp && /tmp/h/.local/share/uv/tools/deskops/bin/python -c \"import deskops,sldb;print(deskops.__file__, sldb.__file__)\"": rc 0 e imprime /workspace/deskops/deskops/__init__.py y /workspace/sldb/src/sldb/__init__.py (el venv de la herramienta deskops está en $HOME/.local/share/uv/tools/deskops)

## Done When

_Name the observable condition that makes the task complete._

Dentro de un contenedor de la imagen claude del fork con el workspace SLDB_1 montado en /workspace, el hook termina con rc 0, `deskops --help` y `sldb --help` funcionan, y el módulo deskops importado resuelve a /workspace/deskops (editable).
