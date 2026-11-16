from deskops.testing.foreign_suites import run_foreign_suite
REPO = "/mnt/ssd/proyectos/SLDB_1/scion"

def test_missing_package():
    run_foreign_suite(["go", "test", "./cmd/nonexistent_pkg_xyz", "-count=1"], cwd=REPO, timeout=300)

def test_missing_executable():
    run_foreign_suite(["go-does-not-exist-xyz", "test"], cwd=REPO, timeout=30)

def test_shell_metachar_not_interpreted():
    # with a shell, '; true' would make this pass; without one, go sees a bogus package and fails
    run_foreign_suite(["go", "test", "./cmd/nonexistent_pkg_xyz; true"], cwd=REPO, timeout=300)

def test_empty_filter_is_vacuous():
    run_foreign_suite(["go", "test", "./cmd", "-run", "NoSuchTestXYZ", "-count=1"], cwd=REPO, timeout=900)
