#!/usr/bin/env python3
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import importlib.util
import json
import os
import stat
import tempfile
import unittest
import unittest.mock
from contextlib import contextmanager

PROVISION_PATH = os.path.join(os.path.dirname(__file__), "provision.py")
SPEC = importlib.util.spec_from_file_location("pi_provision", PROVISION_PATH)
assert SPEC is not None
provision = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(provision)

scion_harness = provision.sh

SECRET = "sk-test-0123456789abcdef-not-a-real-key"
ALIASES = {
    "small": "deepseek-flash",
    "medium": "deepseek-flash",
    "large": "deepseek-v4-pro",
    "extra-large": "deepseek-v4-pro",
}
HARNESS_CONFIG = {"model_aliases": ALIASES, "no_auth": {"behavior": "drop-to-shell"}}


@contextmanager
def temporary_home(path: str):
    old_home = os.environ.get("HOME")
    os.environ["HOME"] = path
    try:
        yield
    finally:
        if old_home is None:
            os.environ.pop("HOME", None)
        else:
            os.environ["HOME"] = old_home


def _path(home: str, name: str) -> str:
    return os.path.join(home, ".pi", "agent", name)


def _read(home: str, name: str) -> dict:
    with open(_path(home, name), "r", encoding="utf-8") as f:
        return json.load(f)


def _seed(home: str, name: str, content: str) -> None:
    os.makedirs(os.path.dirname(_path(home, name)), exist_ok=True)
    with open(_path(home, name), "w", encoding="utf-8") as f:
        f.write(content)


def _invoke(
    home: str,
    *,
    env_vars: list[str] | None = None,
    explicit_type: str = "",
    auth_file_content: str | None = None,
    scion_model: str | None = None,
    staged: bool = True,
) -> dict:
    """Run provision() in an isolated HOME; return resolved-auth.json."""
    bundle = os.path.join(home, ".scion", "harness")
    os.makedirs(os.path.join(bundle, "inputs"), exist_ok=True)
    candidates: dict = {}
    if staged:
        candidates["env_vars"] = env_vars or []
        if explicit_type:
            candidates["explicit_type"] = explicit_type
        if auth_file_content is not None:
            secret_path = os.path.join(bundle, "secrets", "PI_AUTH")
            os.makedirs(os.path.dirname(secret_path), exist_ok=True)
            with open(secret_path, "w", encoding="utf-8") as f:
                f.write(auth_file_content)
            candidates["file_secret_files"] = {"PI_AUTH": secret_path}
    with open(os.path.join(bundle, "inputs", "auth-candidates.json"), "w", encoding="utf-8") as f:
        json.dump(candidates, f)

    manifest = {
        "harness_bundle_dir": bundle,
        "harness_config": HARNESS_CONFIG,
        "agent_workspace": os.path.join(home, "workspace"),
    }
    env_patch = {} if scion_model is None else {"SCION_MODEL": scion_model}
    with temporary_home(home), unittest.mock.patch.dict(os.environ, env_patch):
        if scion_model is None:
            os.environ.pop("SCION_MODEL", None)
        ctx = scion_harness.ProvisionContext("pi", manifest)
        provision.provision(ctx)
    with open(os.path.join(bundle, "outputs", "resolved-auth.json"), "r", encoding="utf-8") as f:
        return json.load(f)


class ApiKeyModeTest(unittest.TestCase):
    def test_selects_api_key_and_writes_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            auth = _invoke(tmp, env_vars=["DEEPSEEK_API_KEY"])
            self.assertEqual(auth["method"], "api-key")
            self.assertEqual(auth["env_var"], "DEEPSEEK_API_KEY")
            models = _read(tmp, "models.json")
            ds = models["providers"]["deepseek"]
            self.assertEqual(ds["apiKey"], "DEEPSEEK_API_KEY")
            self.assertEqual(ds["baseUrl"], "https://api.deepseek.com/v1")
            self.assertEqual({m["id"] for m in ds["models"]}, {"deepseek-flash", "deepseek-v4-pro"})
            settings = _read(tmp, "settings.json")
            self.assertEqual(settings["defaultProvider"], "deepseek")
            self.assertEqual(settings["defaultModel"], "deepseek-flash")
            self.assertFalse(os.path.exists(_path(tmp, "auth.json")))

    def test_no_secret_value_written(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with unittest.mock.patch.dict(os.environ, {"DEEPSEEK_API_KEY": SECRET}):
                _invoke(tmp, env_vars=["DEEPSEEK_API_KEY"])
            for name in ("models.json", "settings.json"):
                with open(_path(tmp, name), "r", encoding="utf-8") as f:
                    self.assertNotIn(SECRET, f.read())


class AuthFileModeTest(unittest.TestCase):
    def test_installs_auth_file_0600(self) -> None:
        content = json.dumps({"deepseek": {"type": "api_key", "key": "x"}})
        with tempfile.TemporaryDirectory() as tmp:
            auth = _invoke(tmp, explicit_type="auth-file", auth_file_content=content)
            self.assertEqual(auth["method"], "auth-file")
            self.assertTrue(auth["auth_file_written"])
            with open(_path(tmp, "auth.json"), "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), content)
            self.assertEqual(stat.S_IMODE(os.stat(_path(tmp, "auth.json")).st_mode), 0o600)
            self.assertEqual(_read(tmp, "settings.json")["defaultModel"], "deepseek-flash")

    def test_autodetects_auth_file_without_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            auth = _invoke(tmp, auth_file_content="{}")
            self.assertEqual(auth["method"], "auth-file")

    def test_api_key_wins_over_auth_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            auth = _invoke(tmp, env_vars=["DEEPSEEK_API_KEY"], auth_file_content="{}")
            self.assertEqual(auth["method"], "api-key")
            self.assertFalse(os.path.exists(_path(tmp, "auth.json")))

    def test_invalid_auth_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(scion_harness.ProvisionError):
                _invoke(tmp, explicit_type="auth-file", auth_file_content="not json")
            with self.assertRaises(scion_harness.ProvisionError):
                _invoke(tmp, explicit_type="auth-file", auth_file_content="  ")


class NoAuthTest(unittest.TestCase):
    def test_nothing_staged_runs_no_auth(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            auth = _invoke(tmp, staged=False)
            self.assertEqual(auth["method"], "none")
            # The provider config is still written so `pi /login` works.
            self.assertIn("deepseek", _read(tmp, "models.json")["providers"])

    def test_explicit_api_key_without_env_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(scion_harness.ProvisionError):
                _invoke(tmp, explicit_type="api-key")

    def test_unknown_auth_type_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(scion_harness.ProvisionError):
                _invoke(tmp, env_vars=["DEEPSEEK_API_KEY"], explicit_type="vertex-ai")


class ModelTest(unittest.TestCase):
    def _model(self, scion_model: str | None) -> tuple[str, str]:
        with tempfile.TemporaryDirectory() as tmp:
            _invoke(tmp, env_vars=["DEEPSEEK_API_KEY"], scion_model=scion_model)
            s = _read(tmp, "settings.json")
            return s["defaultProvider"], s["defaultModel"]

    def test_default(self) -> None:
        self.assertEqual(self._model(None), ("deepseek", "deepseek-flash"))

    def test_alias_large(self) -> None:
        self.assertEqual(self._model("large"), ("deepseek", "deepseek-v4-pro"))

    def test_alias_shorthand(self) -> None:
        self.assertEqual(self._model("s"), ("deepseek", "deepseek-flash"))

    def test_concrete_model(self) -> None:
        self.assertEqual(self._model("deepseek-v4-pro"), ("deepseek", "deepseek-v4-pro"))

    def test_provider_slash_model(self) -> None:
        self.assertEqual(self._model("openai/gpt-4o"), ("openai", "gpt-4o"))


class MergeAndIdempotencyTest(unittest.TestCase):
    def test_settings_shallow_merge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(tmp, "settings.json", json.dumps({
                "defaultProvider": "google", "defaultModel": "gemini", "theme": "dark",
                "lastChangelogVersion": "9.9.9", "nested": {"a": 1},
            }))
            _invoke(tmp, env_vars=["DEEPSEEK_API_KEY"])
            s = _read(tmp, "settings.json")
            self.assertEqual(s["defaultProvider"], "deepseek")
            self.assertEqual(s["defaultModel"], "deepseek-flash")
            self.assertEqual(s["theme"], "dark")
            self.assertEqual(s["nested"], {"a": 1})
            self.assertEqual(s["lastChangelogVersion"], "9.9.9")

    def test_settings_gets_changelog_version_when_absent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _invoke(tmp, env_vars=["DEEPSEEK_API_KEY"])
            self.assertEqual(_read(tmp, "settings.json")["lastChangelogVersion"], provision.PI_VERSION)

    def test_models_provider_level_merge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(tmp, "models.json", json.dumps({
                "providers": {
                    "ollama": {"baseUrl": "http://localhost:11434/v1"},
                    "deepseek": {"baseUrl": "http://stale", "apiKey": "STALE"},
                },
                "other": True,
            }))
            _invoke(tmp, env_vars=["DEEPSEEK_API_KEY"])
            m = _read(tmp, "models.json")
            self.assertEqual(m["providers"]["ollama"], {"baseUrl": "http://localhost:11434/v1"})
            self.assertEqual(m["providers"]["deepseek"], provision.DEEPSEEK_PROVIDER)
            self.assertTrue(m["other"])

    def test_unusable_json_left_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(tmp, "settings.json", "// jsonc comment\n{}")
            _seed(tmp, "models.json", "[1, 2]")
            _invoke(tmp, env_vars=["DEEPSEEK_API_KEY"])
            with open(_path(tmp, "settings.json"), encoding="utf-8") as f:
                self.assertEqual(f.read(), "// jsonc comment\n{}")
            with open(_path(tmp, "models.json"), encoding="utf-8") as f:
                self.assertEqual(f.read(), "[1, 2]")

    def test_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _invoke(tmp, env_vars=["DEEPSEEK_API_KEY"])
            first = {n: _read(tmp, n) for n in ("settings.json", "models.json")}
            _invoke(tmp, env_vars=["DEEPSEEK_API_KEY"])
            second = {n: _read(tmp, n) for n in ("settings.json", "models.json")}
            self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
