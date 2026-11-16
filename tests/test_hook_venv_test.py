"""Closeout evidence for the task's test venv in hooks/pre-start-deskops.sh (via deskops.testing).

Runs the Validation checks of the task contract, with the workspace mounted at its own path
(not /workspace): ``bash -n`` on the hook; the hook with ``DESKOPS_DESK_ROOT`` pointing at IR,
then ``pytest -n 2`` on IR's tests/test_imports.py and ``task-python`` printing
``sldb.__file__``, asserted inside the container with ``grep -qF``; the hook with an empty
``DESKOPS_DESK_ROOT``, asserting inside that its log says it skips the test venv; and that IR
gets no new files from those runs.

New-files criterion: ``git -C IR status --short --untracked-files=all`` is read before the first
docker run and after the last; the check fails on any ``??`` path that was not there before,
except paths under ``desk/`` or ``.sldb/``, which other agents write concurrently and which
neither the hook (editable installs, *.egg-info) nor pytest writes. The last test needs the
docker runs of this module; run alone, it fails instead of passing vacuously.
``SCION_TEST_WORKSPACE`` overrides the workspace path (default: the parent of this repo).
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from deskops.testing.foreign_suites import run_foreign_suite

SCION = Path(__file__).resolve().parents[1]
WORKSPACE = Path(os.environ.get("SCION_TEST_WORKSPACE") or SCION.parent)
IR = WORKSPACE / "IR"
HOOK = SCION / "hooks" / "pre-start-deskops.sh"
IMAGE = "ghcr.io/jpruizantonia/scion-claude:f6e623c69"

SLDB_INIT = f"{WORKSPACE}/sldb/src/sldb/__init__.py"
SKIP_LOG = "[pre-start-deskops] skipping test venv: DESKOPS_DESK_ROOT='' has no pyproject.toml"
CONCURRENT_PREFIXES = ("desk/", ".sldb/")

# The contract's command, plus the in-container assertion: grep -qF fails the run (rc != 0)
# when task-python does not import sldb from the workspace checkout.
TEST_VENV_SCRIPT = (
    "mkdir -p /tmp/h && bash /hook.sh"
    f" && cd {IR}"
    f" && /tmp/h/.local/bin/pytest -q -n 2 -p no:cacheprovider {IR}/tests/test_imports.py"
    " && out=$(/tmp/h/.local/bin/task-python -c 'import xdist, sldb, yaml; print(sldb.__file__)')"
    ' && echo "$out"'
    f' && grep -qF {SLDB_INIT} <<<"$out"'
)
SKIP_SCRIPT = (
    'mkdir -p /tmp/h && log=$(bash /hook.sh 2>&1); rc=$?; echo "$log"'
    f' && [ "$rc" = 0 ] && grep -qF "{SKIP_LOG}" <<<"$log"'
)

_STATE: dict[str, object] = {"before": None, "runs": 0}


def _ir_untracked() -> set[str]:
    out = subprocess.run(
        ["git", "-C", str(IR), "status", "--short", "--untracked-files=all"],
        capture_output=True, text=True, check=True,
    ).stdout
    return {line[3:] for line in out.splitlines() if line.startswith("?? ")}


@pytest.fixture
def ir_snapshot() -> None:
    if _STATE["before"] is None:
        _STATE["before"] = _ir_untracked()
    yield
    _STATE["runs"] = int(_STATE["runs"]) + 1


def _docker(desk_root: str, script: str) -> list[str]:
    return [
        "timeout", "900",
        "docker", "run", "--rm",
        "--entrypoint", "bash",
        "--user", "1001:1003",
        "-e", "HOME=/tmp/h",
        "-e", "TMPDIR=/dev/shm",
        "-e", f"SCION_WORKSPACE={WORKSPACE}",
        "-e", f"DESKOPS_DESK_ROOT={desk_root}",
        "-v", "/dev/shm:/dev/shm",
        "-v", f"{WORKSPACE}:{WORKSPACE}",
        "-v", f"{HOOK}:/hook.sh:ro",
        IMAGE,
        "-c", script,
    ]


def test_hook_parses() -> None:
    run_foreign_suite(["bash", "-n", str(HOOK)], cwd=SCION)


def test_hook_builds_task_test_venv_for_ir(ir_snapshot: None) -> None:
    run_foreign_suite(_docker(str(IR), TEST_VENV_SCRIPT), cwd=SCION, timeout=960)


def test_hook_skips_test_venv_without_desk_root(ir_snapshot: None) -> None:
    run_foreign_suite(_docker("", SKIP_SCRIPT), cwd=SCION, timeout=960)


def test_ir_gets_no_new_files() -> None:
    if int(_STATE["runs"]) < 2 or _STATE["before"] is None:
        pytest.fail("run the whole module: this check compares IR before and after the docker runs")
    new = sorted(
        path for path in _ir_untracked() - set(_STATE["before"])  # type: ignore[arg-type]
        if not path.startswith(CONCURRENT_PREFIXES)
    )
    assert not new, f"new untracked files in {IR}: {new}"
