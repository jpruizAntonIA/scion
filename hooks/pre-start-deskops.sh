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
# installs both packages as uv tools. Nothing is written into the checkout.
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

# Build from throwaway copies: setuptools writes *.egg-info next to the sources,
# and the shared checkout is not ours to dirty (nor writable when mounted ro).
BUILD_DIR="$(mktemp -d "${TMPDIR:-/tmp}/deskops-tools.XXXXXX")"
trap 'rm -rf "$BUILD_DIR"' EXIT
for name in sldb deskops; do
  mkdir -p "$BUILD_DIR/$name"
  tar -C "$WORKSPACE/$name" \
    --exclude=.git --exclude=.sldb --exclude=node_modules --exclude=.venv \
    --exclude=runs --exclude=.tmp --exclude='*.egg-info' --exclude=__pycache__ \
    -cf - . | tar -C "$BUILD_DIR/$name" -xf -
done

# uv tool install = one isolated venv per tool, entry points in $TOOL_BIN.
# deskops imports sldb, so sldb goes into the deskops venv too (--with).
"$UV" tool install --quiet --python "$PYTHON_SPEC" --reinstall "$BUILD_DIR/sldb"
"$UV" tool install --quiet --python "$PYTHON_SPEC" --reinstall --with "$BUILD_DIR/sldb" "$BUILD_DIR/deskops"

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
