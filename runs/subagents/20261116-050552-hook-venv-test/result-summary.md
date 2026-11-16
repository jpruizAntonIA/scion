# result-summary — run-deskops-e-a6de4211680d (executor, attempt 1)

Task: task-hook-deskops-tools-venv-de-test-del-repo-de-la-tarea-pytest-pytest-xdist-y-extras-de-test-dentro-del
Status: implemented and validated; **uncommitted** (only `hooks/pre-start-deskops.sh` is modified).

## What changed

New block in `hooks/pre-start-deskops.sh`, after the `uv tool install` lines and the check that sldb/deskops landed,
before the PATH/rc section and the `ready` log:

- `TASK_ROOT=${DESKOPS_DESK_ROOT:-}`; if it has no `pyproject.toml` → log `skipping test venv: ...` and continue (rc 0).
- Picks EXTRA with uv's Python + `tomllib`: `test` if it is in `[project.optional-dependencies]`, else `dev`, else none.
- `uv venv --allow-existing $HOME/.venvs/task`; `uv pip install -e "$TASK_ROOT[$EXTRA]" -e "$SLDB_SRC[mcp,code]" pytest-xdist==3.8.0`
  (no brackets when EXTRA is empty). If the venv or the install fails → log and `exit 1`.
- `$TOOL_BIN/pytest` → symlink to `$HOME/.venvs/task/bin/pytest`.
- `$TOOL_BIN/task-python` → **a 2-line sh wrapper** (`exec "$HOME/.venvs/task/bin/python" "$@"`), not a symlink. See deviation.
- Log: venv path, task root and chosen extra.

The runuser re-exec as the workload user (748443c83), the hook's own uv, and PYTHON_SPEC are unchanged.

```diff
diff --git a/hooks/pre-start-deskops.sh b/hooks/pre-start-deskops.sh
index 9ba946b80..b2f992b72 100755
--- a/hooks/pre-start-deskops.sh
+++ b/hooks/pre-start-deskops.sh
@@ -76,6 +76,45 @@ for tool in sldb deskops; do
   fi
 done
 
+# Test venv for the task's repo ($DESKOPS_DESK_ROOT, set by the deskops scion
+# template): the tool venvs above carry neither pytest nor the repo's deps, so
+# an executor could not run `pytest -n N` without a hand-made PYTHONPATH.
+# $HOME/.venvs/task gets the repo editable with its test extra (else dev, else
+# none), sldb editable with [mcp,code], and pytest-xdist; `pytest` and
+# `task-python` in $TOOL_BIN point at it. Editable installs may write *.egg-info
+# next to the sources; nothing else is written into the task repo.
+TASK_ROOT="${DESKOPS_DESK_ROOT:-}"
+if [ -n "$TASK_ROOT" ] && [ -f "$TASK_ROOT/pyproject.toml" ]; then
+  TASK_VENV="$HOME/.venvs/task"
+  if ! EXTRA="$("$UV" run --quiet --no-project --python "$PYTHON_SPEC" python -c '
+import sys, tomllib
+with open(sys.argv[1], "rb") as fh:
+    extras = tomllib.load(fh).get("project", {}).get("optional-dependencies", {})
+print(next((name for name in ("test", "dev") if name in extras), ""))
+' "$TASK_ROOT/pyproject.toml")"; then
+    log "cannot read $TASK_ROOT/pyproject.toml to pick the test extra"
+    exit 1
+  fi
+  TASK_SPEC="$TASK_ROOT"
+  [ -n "$EXTRA" ] && TASK_SPEC="$TASK_ROOT[$EXTRA]"
+  if ! "$UV" venv --quiet --python "$PYTHON_SPEC" --allow-existing "$TASK_VENV" \
+    || ! "$UV" pip install --quiet --python "$TASK_VENV/bin/python" \
+      -e "$TASK_SPEC" -e "$SLDB_SRC[mcp,code]" pytest-xdist==3.8.0; then
+    log "test venv install failed for $TASK_SPEC in $TASK_VENV"
+    exit 1
+  fi
+  ln -sf "$TASK_VENV/bin/pytest" "$TOOL_BIN/pytest"
+  # Not a symlink: Python finds pyvenv.cfg next to the path it was started
+  # from, and a symlink in $TOOL_BIN resolves past the venv to the base
+  # interpreter, which would run without the venv's packages.
+  rm -f "$TOOL_BIN/task-python"
+  printf '#!/bin/sh\nexec "%s/bin/python" "$@"\n' "$TASK_VENV" > "$TOOL_BIN/task-python"
+  chmod +x "$TOOL_BIN/task-python"
+  log "test venv: $TASK_VENV for $TASK_ROOT (extra: ${EXTRA:-none}); pytest and task-python in $TOOL_BIN"
+else
+  log "skipping test venv: DESKOPS_DESK_ROOT='$TASK_ROOT' has no pyproject.toml"
+fi
+
 # Make the entry points reachable for the harness process: shell rc files for
 # login/interactive shells, a symlink in /usr/local/bin when it is writable.
 PATH_LINE="export PATH=\"$TOOL_BIN:\$PATH\""
```

## What I ran (detail in validation.log)

1. `bash -n hooks/pre-start-deskops.sh` → rc 0.
2. The contract's docker run with `DESKOPS_DESK_ROOT=/mnt/ssd/proyectos/SLDB_1/IR` (scion-claude:f6e623c69, `--rm`):
   - attempt 1 → rc 1: hook OK, `pytest -n 2` 9 passed, but `task-python -c 'import xdist…'` → `ModuleNotFoundError: xdist`.
     Cause: with `task-python` as a symlink, CPython follows the chain
     (`task-python` → `.venvs/task/bin/python` → `/usr/bin/python3.13`) and finds no `pyvenv.cfg`, so it runs the base interpreter without the venv.
   - Fixed with the wrapper; reran from 1. → rc 0: `extra: test`, `9 passed`, prints `/mnt/ssd/proyectos/SLDB_1/sldb/src/sldb/__init__.py`. Output in docker-ir.out.
3. Same docker run with `-e DESKOPS_DESK_ROOT=` and only `bash /hook.sh` → rc 0, log
   `skipping test venv: DESKOPS_DESK_ROOT='' has no pyproject.toml`. Output in docker-empty.out.
4. `git -C /mnt/ssd/proyectos/SLDB_1/IR status --short` before and after (ir-status-before.txt / ir-status-after.txt / ir-status.diff).
   The hook added nothing. The diff does show 3 entries, all from concurrent IR activity that is not mine:
   ` M` on the IR13 TaskCodeDoc and its desk/tasks md, plus `?? runs/subagents/20261116-050927/` (holds `context-review/`, a deskops review run).
   There are no new `egg-info` or `__pycache__` entries.
5. `/dev/shm`: listing before and after is identical (nothing left behind).

## For the coordinator to review

- **Deviation from the contract:** `task-python` is a wrapper script, not a symlink ("enlaces ... que apuntan a ese venv").
  As a symlink it fails the contract's own validation (see 2). `pytest` is still a symlink; that works because its shebang
  points at the venv python. Accept the deviation, or rewrite the contract.
- **False premise in the contract:** it says the task repo ignores `*.egg-info` in .gitignore. sldb does; **IR does not**.
  `IR/.gitignore` has only `.sldb_cache/`, `.deskops.log` and `runs/subagents/*/session.jsonl`. `src/specir.egg-info/` and
  the `__pycache__/` dirs were already untracked in IR before my runs (ir-status-before.txt), so the validation holds:
  nothing new. On a fresh IR checkout, though, the editable install would create `src/specir.egg-info/` untracked.
  Suggestion (outside this task's scope): add `*.egg-info/` and `__pycache__/` to IR/.gitignore.
- In the container, `PYTHON_SPEC=3.13` resolves to the image's `/usr/bin/python3.13`.
- Not done (out of scope per the contract): `scion project hook update` on the hub, commit, closeout.
