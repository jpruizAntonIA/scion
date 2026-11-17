"""Closeout evidence for the IR executor template task: runs its deskops tests in the clean deskops checkout."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from deskops.testing.foreign_suites import run_foreign_suite

DESKOPS = Path(os.environ.get("DESKOPS_TEST_CHECKOUT", "/mnt/ssd/herramientas/deskops"))
SLDB = Path(os.environ.get("SLDB_TEST_CHECKOUT", "/mnt/ssd/herramientas/sldb"))
REQUIRED_COMMITS = ("4a7707a5", "4c745c18", "881e177a")
TIMEOUT = 600
GOLDENS_TIMEOUT = 1200


def _env() -> dict[str, str]:
    env = dict(os.environ)
    env.setdefault("TMPDIR", "/dev/shm")
    return env


def _pytest(*args: str) -> list[str]:
    return [
        "uv", "run", "--no-project",
        "--with", "pytest",
        "--with-editable", str(DESKOPS),
        "--with-editable", str(SLDB),
        "python", "-m", "pytest", "-q", "-p", "no:cacheprovider", *args,
    ]


@pytest.fixture(scope="module", autouse=True)
def _checkout_has_the_task_commits() -> None:
    for commit in REQUIRED_COMMITS:
        run_foreign_suite(
            ["git", "merge-base", "--is-ancestor", commit, "HEAD"], cwd=DESKOPS, timeout=60, env=_env()
        )


def test_scion_runtime_passes() -> None:
    run_foreign_suite(_pytest("tests/test_scion_runtime.py"), cwd=DESKOPS, timeout=TIMEOUT, env=_env())


def test_role_runtime_artifacts_passes() -> None:
    run_foreign_suite(_pytest("tests/test_role_runtime_artifacts.py"), cwd=DESKOPS, timeout=TIMEOUT, env=_env())


def test_command_registry_passes() -> None:
    run_foreign_suite(_pytest("tests/test_command_registry.py"), cwd=DESKOPS, timeout=TIMEOUT, env=_env())


def test_help_goldens_pass() -> None:
    run_foreign_suite(
        _pytest("tests/test_output_goldens.py", "-k", "test_help_goldens"),
        cwd=DESKOPS,
        timeout=GOLDENS_TIMEOUT,
        env=_env(),
    )
