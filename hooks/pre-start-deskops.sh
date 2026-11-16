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

# Scion runs project pre-start hooks as root (sciontool is PID 1 and only drops
# privileges for the harness). Installed as root, uv leaves root-owned files in
# the agent home, which is bind-mounted from the host (so `scion delete` cannot
# remove it: "permission denied"), and a root-owned PKG-INFO in the workspace
# egg-info. So, as root, the hook re-runs itself as the workload user for the
# install, and keeps only the /usr/local/bin links for root.
WORKLOAD_USER="${SCION_WORKLOAD_USER:-scion}"
if [ "$(id -u)" = 0 ] && [ -z "${PRE_START_DESKOPS_AS_USER:-}" ] && id "$WORKLOAD_USER" >/dev/null 2>&1; then
  runuser -u "$WORKLOAD_USER" -- env PRE_START_DESKOPS_AS_USER=1 HOME="$HOME" PATH="$PATH" bash "$0" "$@"
  for tool in sldb deskops; do
    [ -e "/usr/local/bin/$tool" ] || ln -s "$HOME/.local/bin/$tool" "/usr/local/bin/$tool"
  done
  exit 0
fi

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

# Test venv for the task's repo ($DESKOPS_DESK_ROOT, set by the deskops scion
# template): the tool venvs above carry neither pytest nor the repo's deps, so
# an executor could not run `pytest -n N` without a hand-made PYTHONPATH.
# $HOME/.venvs/task gets the repo editable with its test extra (else dev, else
# none), sldb editable with [mcp,code], and pytest-xdist; `pytest` and
# `task-python` in $TOOL_BIN point at it. Editable installs may write *.egg-info
# next to the sources; nothing else is written into the task repo.
TASK_ROOT="${DESKOPS_DESK_ROOT:-}"
if [ -n "$TASK_ROOT" ] && [ -f "$TASK_ROOT/pyproject.toml" ]; then
  TASK_VENV="$HOME/.venvs/task"
  if ! EXTRA="$("$UV" run --quiet --no-project --python "$PYTHON_SPEC" python -c '
import sys, tomllib
with open(sys.argv[1], "rb") as fh:
    extras = tomllib.load(fh).get("project", {}).get("optional-dependencies", {})
print(next((name for name in ("test", "dev") if name in extras), ""))
' "$TASK_ROOT/pyproject.toml")"; then
    log "cannot read $TASK_ROOT/pyproject.toml to pick the test extra"
    exit 1
  fi
  TASK_SPEC="$TASK_ROOT"
  [ -n "$EXTRA" ] && TASK_SPEC="$TASK_ROOT[$EXTRA]"
  if ! "$UV" venv --quiet --python "$PYTHON_SPEC" --allow-existing "$TASK_VENV" \
    || ! "$UV" pip install --quiet --python "$TASK_VENV/bin/python" \
      -e "$TASK_SPEC" -e "$SLDB_SRC[mcp,code]" pytest-xdist==3.8.0; then
    log "test venv install failed for $TASK_SPEC in $TASK_VENV"
    exit 1
  fi
  ln -sf "$TASK_VENV/bin/pytest" "$TOOL_BIN/pytest"
  # Not a symlink: Python finds pyvenv.cfg next to the path it was started
  # from, and a symlink in $TOOL_BIN resolves past the venv to the base
  # interpreter, which would run without the venv's packages.
  rm -f "$TOOL_BIN/task-python"
  printf '#!/bin/sh\nexec "%s/bin/python" "$@"\n' "$TASK_VENV" > "$TOOL_BIN/task-python"
  chmod +x "$TOOL_BIN/task-python"
  log "test venv: $TASK_VENV for $TASK_ROOT (extra: ${EXTRA:-none}); pytest and task-python in $TOOL_BIN"
else
  log "skipping test venv: DESKOPS_DESK_ROOT='$TASK_ROOT' has no pyproject.toml"
fi

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
