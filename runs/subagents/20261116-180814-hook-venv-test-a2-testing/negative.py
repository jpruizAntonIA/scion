import subprocess, sys, ast, pathlib
src = pathlib.Path("tests/test_hook_venv_test.py").read_text()
ns = {"__name__": "x"}
# evaluate only the constants (avoid importing deskops/pytest)
tree = ast.parse(src)
keep = [n for n in tree.body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") in
        {"SCION","WORKSPACE","IR","HOOK","IMAGE","SLDB_INIT","SKIP_LOG","CONCURRENT_PREFIXES","TEST_VENV_SCRIPT","SKIP_SCRIPT"}]
mod = ast.Module(body=[ast.parse("import os\nfrom pathlib import Path\n__file__=%r" % str(pathlib.Path("tests/test_hook_venv_test.py").resolve())).body[0],
                       *ast.parse("import os\nfrom pathlib import Path\n__file__=%r" % str(pathlib.Path("tests/test_hook_venv_test.py").resolve())).body[1:], *keep], type_ignores=[])
exec(compile(mod, "consts", "exec"), ns)
d = sys.argv[1]
def run(name, hook_body, script):
    hp = f"{d}/{name}.sh"; pathlib.Path(hp).write_text(hook_body)
    s = script.replace("/hook.sh", hp).replace("mkdir -p /tmp/h", f"mkdir -p {d}/h")
    r = subprocess.run(["bash", "-c", s], capture_output=True, text=True)
    print(f"{name}: rc={r.returncode} out={r.stdout.strip()!r}")
    return r.returncode
print("SKIP_LOG:", ns["SKIP_LOG"])
pos = run("skip-real-text", f"echo {ns['SKIP_LOG']!r}\n", ns["SKIP_SCRIPT"])
neg1 = run("skip-other-text", "echo '[pre-start-deskops] test venv: built'\n", ns["SKIP_SCRIPT"])
neg2 = run("skip-right-text-rc1", f"echo {ns['SKIP_LOG']!r}; exit 1\n", ns["SKIP_SCRIPT"])
# real hook's printf format applied to empty TASK_ROOT, outside docker: only the log line
real = "TASK_ROOT=''\nlog() { printf '[pre-start-deskops] %s\\n' \"$*\"; }\nlog \"skipping test venv: DESKOPS_DESK_ROOT='$TASK_ROOT' has no pyproject.toml\"\n"
pos2 = run("skip-hook-log-format", real, ns["SKIP_SCRIPT"])
# TEST_VENV grep negative: fake hook installs fake pytest/task-python under h/.local/bin
tv = ns["TEST_VENV_SCRIPT"].replace(str(ns["IR"]), d).replace("/tmp/h", f"{d}/h")
def fake(name, printed):
    body = f"mkdir -p {d}/h/.local/bin\nprintf '#!/bin/sh\\nexit 0\\n' > {d}/h/.local/bin/pytest\nprintf '#!/bin/sh\\necho {printed}\\n' > {d}/h/.local/bin/task-python\nchmod +x {d}/h/.local/bin/*\n"
    return run(name, body, tv)
pos3 = fake("venv-right-path", ns["SLDB_INIT"])
neg3 = fake("venv-wrong-path", "/tmp/h/.venvs/task/lib/python3.12/site-packages/sldb/__init__.py")
ok = pos == 0 and pos2 == 0 and pos3 == 0 and neg1 != 0 and neg2 != 0 and neg3 != 0
print("NEGATIVE-CHECKS", "PASS" if ok else "FAIL")
