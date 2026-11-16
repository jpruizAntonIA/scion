"""Closeout evidence for the hub agent-only API listener: runs its Go tests and go vet on ./cmd."""

from __future__ import annotations

import os
from pathlib import Path

from deskops.testing.foreign_suites import run_foreign_suite

REPO_ROOT = Path(__file__).resolve().parents[1]
TIMEOUT = 900


def _env() -> dict[str, str]:
    env = dict(os.environ)
    env.setdefault("GOCACHE", "/mnt/ssd/cache/go-build")
    env.setdefault("GOMODCACHE", "/mnt/ssd/cache/go-mod")
    env.setdefault("TMPDIR", "/dev/shm")
    return env


def test_go_hub_agent_api_tests_pass() -> None:
    run_foreign_suite(
        ["go", "test", "./cmd", "-run", "ContainerHubEndpoint|AgentAPI", "-count=1"],
        cwd=REPO_ROOT,
        timeout=TIMEOUT,
        env=_env(),
    )


def test_go_vet_cmd_passes() -> None:
    run_foreign_suite(["go", "vet", "./cmd"], cwd=REPO_ROOT, timeout=TIMEOUT, env=_env())
