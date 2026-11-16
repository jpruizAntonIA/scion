---
sldb:
  by: agent
  at: '2026-11-16T05:03:41Z'
  authority: generated
  via: save_document_payload
id: task-hook-deskops-tools-venv-de-test-del-repo-de-la-tarea-pytest-pytest-xdist-y-extras-de-test-dentro-del
status: draft
summary: ''
tags:
- workspace:desk
- artifact:task
- host:robocop2
current_node: ritual-execution
history: []
references:
- desk/inbox/20261116-011045-suggestion-piloto-scion-fase-1-el-hook-deskops-tools-no-instala-los-extras-de-test-ni-pi.md
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

# Hook deskops-tools: venv de test del repo de la tarea (pytest, pytest-xdist y extras de test) dentro del contenedor

## Rationale

_Explain why this task exists or the business driver behind it._

En la fase 1 del piloto scion en IR (nota de deskops desk/inbox/20261116-011045 de este desk, origen deskops desk/inbox/20261116-002453, brecha 4) el ejecutor claude en contenedor no tenía pytest ni pytest-xdist: el hook hooks/pre-start-deskops.sh solo instala las herramientas sldb y deskops (uv tool install --editable, líneas 69-70), cuyos venvs no traen pytest ni las dependencias del repo de la tarea. El ejecutor improvisó un PYTHONPATH con el .venv de IR y los site-packages del tool sldb. Las reglas de la máquina piden correr las suites con pytest -n 4 (xdist).

## Goal

_Describe the concrete result this task must produce._

Al terminar el hook, dentro del contenedor existe un venv de test del repo de la tarea en $HOME/.venvs/task, con ese repo instalado editable con su extra de test, sldb editable con los extras mcp y code, pytest-xdist==3.8.0, y enlaces pytest y task-python en $HOME/.local/bin que apuntan a ese venv. Con eso, cd $DESKOPS_DESK_ROOT && pytest -q -n 2 <archivo> funciona sin PYTHONPATH a mano.

## Scope

_State what is in scope and what is out of scope._

IN: solo hooks/pre-start-deskops.sh, un bloque nuevo después de los uv tool install de sldb y deskops (líneas 69-70) y antes del log ready. Repo de la tarea = $DESKOPS_DESK_ROOT (lo pone el template scion de deskops, p. ej. /mnt/ssd/proyectos/SLDB_1/IR en IR/.scion/templates/ir-executor/scion-agent.yaml). Si DESKOPS_DESK_ROOT está vacío o no tiene pyproject.toml, el bloque se salta con un log y el hook sigue (rc 0). Extra a instalar: test si el pyproject lo declara en [project.optional-dependencies], si no dev, si no ninguno (IR declara test; sldb y deskops declaran dev). Se mantiene todo lo existente: re-ejecución como el usuario del agente con runuser cuando corre como root (commit 748443c83), uv propio, PYTHON_SPEC. OUT: instalar pi o cualquier secret en el hook (brecha 1 de la misma nota: se descarta acá; la alternativa la cubre la tarea de deskops task-deskops-review-puede-correr-con-un-runtimeprofiledoc-de-claude-cuando-pi-no-esta-disponible), cambiar la imagen, cambiar los templates de deskops, re-registrar el hook en el hub de producción (scion project hook update lo hace el coordinador de la fase 1 cuando se retome).

## Implementation Path

_Outline the expected implementation route or affected surface._

Variables que el hook ya define y se reutilizan: SLDB_SRC=$WORKSPACE/sldb (línea 35), TOOL_BIN=$HOME/.local/bin (línea 39, ya existe porque uv tool install deja ahí sldb y deskops), UV y PYTHON_SPEC. En hooks/pre-start-deskops.sh, tras la línea 70: TASK_ROOT=${DESKOPS_DESK_ROOT:-}; si [ -f "$TASK_ROOT/pyproject.toml" ]: elegir EXTRA leyendo el pyproject con el python de uv ("$UV" run --no-project --python "$PYTHON_SPEC" python -c con tomllib: test si está en project.optional-dependencies, si no dev, si no vacío); "$UV" venv --quiet --python "$PYTHON_SPEC" --allow-existing "$HOME/.venvs/task"; "$UV" pip install --quiet --python "$HOME/.venvs/task/bin/python" -e "$TASK_ROOT[$EXTRA]" (sin corchetes si EXTRA vacío) -e "$SLDB_SRC[mcp,code]" pytest-xdist==3.8.0; ln -sf "$HOME/.venvs/task/bin/pytest" "$TOOL_BIN/pytest"; ln -sf "$HOME/.venvs/task/bin/python" "$TOOL_BIN/task-python"; log con la ruta y el extra elegido. Si la instalación falla, log y exit 1 (un ejecutor sin entorno de test no debe arrancar en silencio). La instalación editable puede escribir *.egg-info dentro de $TASK_ROOT y de $SLDB_SRC: está permitido porque esos repos lo ignoran en .gitignore; fuera de eso el hook no escribe en $TASK_ROOT.

## Validation

_List the checks required before this task can close._

- bash -n hooks/pre-start-deskops.sh
- timeout 900 docker run --rm --entrypoint bash --user 1001:1003 -e HOME=/tmp/h -e TMPDIR=/dev/shm -e SCION_WORKSPACE=/mnt/ssd/proyectos/SLDB_1 -e DESKOPS_DESK_ROOT=/mnt/ssd/proyectos/SLDB_1/IR -v /dev/shm:/dev/shm -v /mnt/ssd/proyectos/SLDB_1:/mnt/ssd/proyectos/SLDB_1 -v /mnt/ssd/proyectos/SLDB_1/scion/hooks/pre-start-deskops.sh:/hook.sh:ro ghcr.io/jpruizantonia/scion-claude:f6e623c69 -c "mkdir -p /tmp/h && bash /hook.sh && cd /mnt/ssd/proyectos/SLDB_1/IR && /tmp/h/.local/bin/pytest -q -n 2 -p no:cacheprovider /mnt/ssd/proyectos/SLDB_1/IR/tests/test_imports.py && /tmp/h/.local/bin/task-python -c 'import xdist, sldb, yaml; print(sldb.__file__)'": rc 0, los tests pasan e imprime /mnt/ssd/proyectos/SLDB_1/sldb/src/sldb/__init__.py (-n 2 porque el contenedor tiene cpu_limit 2; en el host las suites usan -n 4)
- Mismo docker run con -e DESKOPS_DESK_ROOT= (vacío) y el comando reducido a bash /hook.sh: rc 0 y el log dice que salta el venv de test
- git -C /mnt/ssd/proyectos/SLDB_1/IR status --short no muestra archivos nuevos tras las corridas

## Done When

_Name the observable condition that makes the task complete._

El hook commiteado en main de este repo deja, con DESKOPS_DESK_ROOT apuntando a IR, un pytest con xdist que corre /mnt/ssd/proyectos/SLDB_1/IR/tests/test_imports.py en verde dentro de scion-claude:f6e623c69 sin PYTHONPATH manual; con DESKOPS_DESK_ROOT vacío el hook sigue terminando en rc 0; IR queda sin archivos nuevos.
