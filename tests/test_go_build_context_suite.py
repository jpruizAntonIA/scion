"""Closeout evidence for `scion build` streaming the build context on stdin.

Runs the Go tests of cmd/build_context_test.go (localBuildArgs and
writeBuildContextTar) through deskops.testing.foreign_suites; pytest fails when
`go test` fails. Run from the repository root:

    TMPDIR=/dev/shm uv run --no-project --with pytest \
        --with-editable /mnt/ssd/herramientas/deskops \
        python -m pytest -q tests/test_go_build_context_suite.py
"""

from pathlib import Path

from deskops.testing.foreign_suites import run_foreign_suite

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_go_build_context_suite() -> None:
    run_foreign_suite(
        ["go", "test", "./cmd", "-run", "TestLocalBuildArgs|TestWriteBuildContextTar", "-count=1"],
        cwd=REPO_ROOT,
        timeout=900,
    )
