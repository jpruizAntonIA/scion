FILE:desk/tasks/task-fase-0-ir-hook-pre-start-deskops-tools-instala-sldb-y-deskops-editables-desde-workspace.md
---
sldb:
  by: agent
  at: '2026-11-16T00:45:33Z'
  authority: generated
  via: create_document
id: task-fase-0-ir-hook-pre-start-deskops-tools-instala-sldb-y-deskops-editables-desde-workspace
status: draft
summary: ''
tags:
- workspace:desk
- artifact:task
current_node: ritual-execution
history: []
references: []
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

IN: hooks/pre-start-deskops.sh (instalación y comentarios). Se mantiene: uv propio, Python 3.13, salida no cero si falta una herramienta, PATH en .profile/.bashrc. Los *.egg-info que escribe setuptools junto a las fuentes están ignorados por git en sldb y deskops. OUT: registrar el hook en el hub (`scion project hook create --name 'deskops tools' --script scion/hooks/pre-start-deskops.sh --project <proyecto>`) es un paso de la fase 1 con el hub del fork; imágenes; código de sldb/deskops.

## Implementation Path

_Outline the expected implementation route or affected surface._

Reemplazar el bloque de copias (mktemp + tar) por dos `uv tool install --quiet --python $PYTHON_SPEC --reinstall --editable ...`.

## Validation

_List the checks required before this task can close._

- bash -n hooks/pre-start-deskops.sh
- docker run (imagen claude del fork, workspace en /workspace) ejecuta el hook: rc 0; python del venv de deskops imprime deskops.__file__ bajo /workspace/deskops y sldb.__file__ bajo /workspace/sldb/src

## Done When

_Name the observable condition that makes the task complete._

Dentro de un contenedor de la imagen claude del fork con el workspace SLDB_1 montado en /workspace, el hook termina con rc 0, `deskops --help` y `sldb --help` funcionan, y el módulo deskops importado resuelve a /workspace/deskops (editable).

FILE:instruccion
Preflight solo-TaskDoc de la tarea task-fase-0-ir-hook-pre-start-deskops-tools-instala-sldb-y-deskops-editables-desde-workspace: reformula el encargo tal como lo leería un ejecutor sin ningún otro contexto, lista ambigüedades con cita textual del input y da el DRY-RUN sin ejecutar nada. No ejecutes nada.

