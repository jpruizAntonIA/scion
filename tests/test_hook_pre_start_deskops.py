"""Closeout evidence for hooks/pre-start-deskops.sh (bash + docker, run through deskops.testing).

Runs the Validation checks of the task contract: ``bash -n`` on the hook, and the hook
inside the fork's claude image with the SLDB_1 workspace mounted at /workspace, asserting
inside the container that deskops and sldb import from /workspace (editable) and that
``deskops --help`` and ``sldb --help`` run. ``SCION_TEST_WORKSPACE`` overrides the
workspace path (default: the parent of this repo).
"""

from __future__ import annotations

import os
from pathlib import Path

from deskops.testing.foreign_suites import run_foreign_suite

SCION = Path(__file__).resolve().parents[1]
WORKSPACE = Path(os.environ.get("SCION_TEST_WORKSPACE") or SCION.parent)
HOOK = SCION / "hooks" / "pre-start-deskops.sh"
IMAGE = "ghcr.io/jpruizantonia/scion-claude:f6e623c69"

DESKOPS_INIT = "/workspace/deskops/deskops/__init__.py"
SLDB_INIT = "/workspace/sldb/src/sldb/__init__.py"

# The contract's command, plus in-container assertions: grep -q fails the run (rc != 0)
# when an import does not resolve to /workspace, so the bridge stays the judge.
CONTAINER_SCRIPT = (
    "mkdir -p /tmp/h && bash /hook.sh && cd /tmp"
    " && out=$(/tmp/h/.local/share/uv/tools/deskops/bin/python -c"
    ' "import deskops,sldb;print(deskops.__file__, sldb.__file__)")'
    ' && echo "$out"'
    f' && grep -qF {DESKOPS_INIT} <<<"$out"'
    f' && grep -qF {SLDB_INIT} <<<"$out"'
    " && /tmp/h/.local/bin/deskops --help >/dev/null"
    " && /tmp/h/.local/bin/sldb --help >/dev/null"
)


def test_hook_parses() -> None:
    run_foreign_suite(["bash", "-n", str(HOOK)], cwd=SCION)


def test_hook_installs_editable_tools_in_claude_image() -> None:
    run_foreign_suite(
        [
            "timeout", "600",
            "docker", "run", "--rm",
            "--entrypoint", "bash",
            "--user", "1001:1003",
            "-e", "HOME=/tmp/h",
            "-e", "SCION_WORKSPACE=/workspace",
            "-v", f"{WORKSPACE}:/workspace",
            "-v", f"{HOOK}:/hook.sh:ro",
            IMAGE,
            "-c", CONTAINER_SCRIPT,
        ],
        cwd=SCION,
        timeout=660,
    )
