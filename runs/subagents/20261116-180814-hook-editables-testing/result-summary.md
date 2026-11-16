# Tester result: task-fase-0-ir-hook-pre-start-deskops-tools-instala-sldb-y-deskops-editables-desde-workspace

- Role: tester (deskops-tester), attempt 1
- Run: run-deskops-t-492f31bb3839, local subagent (not Scion)
- Under test: hooks/pre-start-deskops.sh at main (f6e623c69 + 748443c83 + 56a66098c; unchanged since 56a66098c at HEAD a9cd0d7cd) and the uncommitted tests/test_hook_pre_start_deskops.py (bridge: deskops.testing.foreign_suites.run_foreign_suite)
- Commands and exit codes: validation.log. Outputs: a-bash-n.out, b-docker.out, c-pytest.out, d-negative.out, e1-grep-negative.out, git-status-*.txt/.diff

## Validations

| # | Check | Result |
|---|-------|--------|
| a | `bash -n hooks/pre-start-deskops.sh` | PASS (rc 0) |
| b | Contract docker run, written by hand (image scion-claude:f6e623c69, --user 1001:1003, HOME=/tmp/h, SLDB_1 mounted at /workspace), plus `deskops --help` and `sldb --help` | PASS: rc 0; printed `/workspace/deskops/deskops/__init__.py /workspace/sldb/src/sldb/__init__.py`; both --help commands ran |
| c | `TMPDIR=/dev/shm uv run --no-project --with pytest --with-editable /mnt/ssd/herramientas/deskops python -m pytest -q -p no:cacheprovider tests/test_hook_pre_start_deskops.py` | PASS: rc 0, 2 passed in 76.66s |
| d | Negative: same test with SCION_TEST_WORKSPACE set to an empty /dev/shm dir | PASS: pytest rc 1; test_hook_installs_editable_tools_in_claude_image FAILED, and the message shows the command, `exit code 1` and the hook output `missing /workspace/sldb/pyproject.toml`. The directory was removed afterwards |
| e | Test review | PASS (details below) |
| f | `git status --short` of sldb and deskops before and after | PASS: identical (diff rc 0) in both repos; the existing changes belong to other agents. *.egg-info is git-ignored in both repos (`git check-ignore`: sldb .gitignore:19, deskops .gitignore:8) |

Global: PASS

## Test review (e)

- It runs what the contract asks for: `bash -n` and the contract's docker command, using the same image tag, user, HOME, SCION_WORKSPACE, mounts and venv python path. It also runs `deskops --help` and `sldb --help` (Done When).
- No shell on the host: `run_foreign_suite` takes argv lists and calls `subprocess.run` without shell=True. There is no shell=/os.system/Popen in the test. The only shell is `bash -c` inside the container.
- The assertions really fail: the `grep -qF` steps are joined with `&&` inside the container. I checked separately in the image that a path that does not match gives rc 1 and stops the chain (e1). The negative in (d) showed that the bridge turns a non-zero rc into a pytest failure.
- No example paths: the workspace comes from the repo's parent (or SCION_TEST_WORKSPACE), the hook is the real file, and the two expected paths are the literal ones in the contract.

## Findings (none of them block)

1. Cosmetic: in the hook's `ready:` log line, `uv python find 3.13` reports `/workspace/.venv/bin/python`, the host venv seen through the mount, instead of the tool interpreter. The `deskops --version` part prints only `deskops`. This is log text only; imports and entry points are correct.
2. Coverage gap, outside the contract's Validation: the test runs the hook as a non-root user (--user 1001:1003). It does not cover the path where the hook starts as root and re-runs itself through runuser (748443c83), which is how Scion runs hooks. It also does not cover the DESKOPS_DESK_ROOT test-venv branch from 56a66098c; with this contract the hook logs "skipping test venv".
3. The test depends on Docker, network access (it downloads uv) and the pulled image. It takes about 75s.

I did not read the executor run before testing. I modified no files outside this run_dir and left nothing in /dev/shm.
