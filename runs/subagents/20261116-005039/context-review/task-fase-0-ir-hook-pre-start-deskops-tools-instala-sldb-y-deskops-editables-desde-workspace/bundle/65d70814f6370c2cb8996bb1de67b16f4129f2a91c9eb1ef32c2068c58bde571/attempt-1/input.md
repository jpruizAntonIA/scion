FILE:desk/tasks/task-fase-0-ir-hook-pre-start-deskops-tools-instala-sldb-y-deskops-editables-desde-workspace.md
---
sldb:
  by: agent
  at: '2026-11-16T00:48:47Z'
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

IN: hooks/pre-start-deskops.sh (instalación y comentarios). WORKSPACE=${SCION_WORKSPACE:-/workspace} (variable vacía o ausente -> /workspace, expansión de bash ya existente en el script); PYTHON_SPEC=${DESKOPS_PYTHON:-3.13} (ya existente). Se mantiene: uv propio (si no hay uv, se instala con curl o wget; sin ninguno sale con 1), salida 1 si falta $WORKSPACE/sldb/pyproject.toml o $WORKSPACE/deskops/pyproject.toml, y salida 1 si después de instalar no existen los ejecutables sldb y deskops en $HOME/.local/bin; PATH en .profile/.bashrc. Que *.egg-info está ignorado por git en sldb y deskops es un hecho a verificar (git check-ignore), no una acción: no se toca ningún .gitignore. OUT: registrar el hook en el hub ('scion project hook create --name "deskops tools" --script scion/hooks/pre-start-deskops.sh <proyecto>') es un paso de la fase 1 con el hub del fork; imágenes; código de sldb/deskops.

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

FILE:desk/rituals/phase.md
---
id: ritual-phase
steps: []
tags:
- workspace:desk
---

# Phase ritual for dependency-layer execution

Run one horizontal layer of scion tasks whose prerequisites are satisfied and whose
planned changes do not overlap, then close the layer with integration validation,
pill reconciliation, and next-phase preparation.

Each task in the phase still closes with its own validation and its own commit;
the phase adds the pass that only makes sense once those tasks are integrated.

FILE:desk/rituals/execution.md
---
id: ritual-execution
steps: []
tags:
- workspace:desk
---

# Execution ritual

Review the board, bind the relevant pills, keep scope tight, and implement only the active task for scion.

FILE:desk/rituals/testing.md
---
id: ritual-testing
steps: []
tags:
- workspace:desk
---

# Testing ritual

Run the smallest relevant validation first, then broaden coverage when scion changes shared behavior.

FILE:desk/rituals/closeout.md
---
id: ritual-closeout
steps: []
tags:
- workspace:desk
---

# Closeout ritual

Close a scion task only after validation passes, any durable knowledge from bound pills is linked to an atom when needed, the board is updated, and the final change is ready to commit.

FILE:hooks/pre-start-deskops.sh
#!/usr/bin/env bash
# Scion project pre-start hook for the SLDB_1 workspace.
#
# Runs inside the agent container before the harness starts (Scion stages it at
# $HOME/.scion/hooks/pre-start.d/30-project-custom). It gives the agent the two
# CLIs a deskops executor needs, `sldb` and `deskops`, installed from the shared
# workspace itself, so `deskops --help` works on the agent's first turn.
#
# The stock harness images ship Python 3.11 without pip; sldb and deskops need
# 3.12+. So the hook installs `uv`, lets uv fetch a Python 3.13 of its own, and
# installs both packages as editable uv tools from the workspace checkouts.
# A non-zero exit aborts the agent start, on purpose: an executor without its
# tools is not an executor, and a silent fallback would hide that.
#
# Registered with:  scion project hook create --name "deskops tools" --script scion/hooks/pre-start-deskops.sh
# Source of truth:  this file in the scion fork; edit it, then `scion project hook update deskops-tools --script ...`.
set -euo pipefail

WORKSPACE="${SCION_WORKSPACE:-/workspace}"
SLDB_SRC="$WORKSPACE/sldb"
DESKOPS_SRC="$WORKSPACE/deskops"
PYTHON_SPEC="${DESKOPS_PYTHON:-3.13}"
UV_BIN="$HOME/.local/bin/uv"
TOOL_BIN="$HOME/.local/bin"

log() { printf '[pre-start-deskops] %s\n' "$*"; }

for dir in "$SLDB_SRC" "$DESKOPS_SRC"; do
  if [ ! -f "$dir/pyproject.toml" ]; then
    log "missing $dir/pyproject.toml: the workspace must be the SLDB_1 root (shared-plain)"
    exit 1
  fi
done

if ! command -v uv >/dev/null 2>&1 && [ ! -x "$UV_BIN" ]; then
  if command -v curl >/dev/null 2>&1; then
    curl -LsSf https://astral.sh/uv/install.sh | env UV_NO_MODIFY_PATH=1 sh >/dev/null
  elif command -v wget >/dev/null 2>&1; then
    wget -qO- https://astral.sh/uv/install.sh | env UV_NO_MODIFY_PATH=1 sh >/dev/null
  else
    log "neither uv, curl nor wget is in the image; cannot install the toolchain"
    exit 1
  fi
fi
UV="$(command -v uv 2>/dev/null || echo "$UV_BIN")"
log "uv $("$UV" --version | awk '{print $2}')"

# Editable installs straight from the shared workspace: a task that changes
# sldb or deskops under /workspace is what the agent runs on its next command,
# with no reinstall. setuptools writes *.egg-info next to the sources; both
# repos ignore it (.gitignore), so the checkouts stay clean for git.
# uv tool install = one isolated venv per tool, entry points in $TOOL_BIN.
# deskops imports sldb, so sldb goes into the deskops venv too, also editable.
"$UV" tool install --quiet --python "$PYTHON_SPEC" --reinstall --editable "$SLDB_SRC"
"$UV" tool install --quiet --python "$PYTHON_SPEC" --reinstall --editable "$DESKOPS_SRC" --with-editable "$SLDB_SRC"

for tool in sldb deskops; do
  if [ ! -x "$TOOL_BIN/$tool" ]; then
    log "$tool did not land in $TOOL_BIN"
    exit 1
  fi
done

# Make the entry points reachable for the harness process: shell rc files for
# login/interactive shells, a symlink in /usr/local/bin when it is writable.
PATH_LINE="export PATH=\"$TOOL_BIN:\$PATH\""
for rc in "$HOME/.profile" "$HOME/.bashrc"; do
  grep -qsF "$PATH_LINE" "$rc" 2>/dev/null || printf '\n%s\n' "$PATH_LINE" >> "$rc"
done
if [ -d /usr/local/bin ] && [ -w /usr/local/bin ]; then
  for tool in sldb deskops; do
    [ -e "/usr/local/bin/$tool" ] || ln -s "$TOOL_BIN/$tool" "/usr/local/bin/$tool"
  done
fi

log "ready: $("$TOOL_BIN/sldb" --version 2>/dev/null || echo sldb) · $("$TOOL_BIN/deskops" --version 2>/dev/null || echo deskops) · python $("$UV" python find "$PYTHON_SPEC" 2>/dev/null || echo "$PYTHON_SPEC")"

FILE:instruccion
Cold-bundle de la tarea task-fase-0-ir-hook-pre-start-deskops-tools-instala-sldb-y-deskops-editables-desde-workspace: con el TaskDoc, los rituales enrutados por el Board, las pills ligadas, los átomos ligados y los archivos que el TaskDoc nombra, reformula el encargo, lista ambigüedades con cita textual del input y da el DRY-RUN sin ejecutar nada. No ejecutes nada.

Sección de validación del TaskDoc:
- bash -n hooks/pre-start-deskops.sh
- docker run (imagen claude del fork, workspace en /workspace) ejecuta el hook: rc 0; python del venv de deskops imprime deskops.__file__ bajo /workspace/deskops y sldb.__file__ bajo /workspace/sldb/src

