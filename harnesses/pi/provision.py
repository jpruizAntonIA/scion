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
"""pi container-side provisioner.

Runs inside the agent container at pre-start (`sciontool harness provision`).
The host has already projected the auth env vars into the harness launch env
(but stripped them from THIS script's env, so we only see their *names* via
inputs/auth-candidates.json) and staged any PI_AUTH file secret.

This script:

  1. Selects the auth method: api-key (DEEPSEEK_API_KEY) > auth-file (PI_AUTH).
  2. Writes ~/.pi/agent/models.json with the DeepSeek provider. Its apiKey is
     the env var NAME "DEEPSEEK_API_KEY": pi resolves it at runtime, so no
     secret value is ever written to disk by this script.
  3. In auth-file mode, installs the staged PI_AUTH secret at
     ~/.pi/agent/auth.json (mode 0600).
  4. Writes ~/.pi/agent/settings.json defaultProvider/defaultModel from the
     resolved model (SCION_MODEL through config.yaml model_aliases, falling
     back to deepseek-flash). Every other existing key is preserved.

Stdlib-only, like every other provisioner.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scion_harness as sh  # noqa: E402

assert sh.INTERFACE_VERSION >= 2, (
    "pi provision.py requires scion_harness INTERFACE_VERSION >= 2; "
    f"got {sh.INTERFACE_VERSION}. Update the staged scion_harness.py."
)

PI_AGENT_DIR = "~/.pi/agent"
PI_AUTH_FILE = PI_AGENT_DIR + "/auth.json"
PI_SETTINGS_FILE = PI_AGENT_DIR + "/settings.json"
PI_MODELS_FILE = PI_AGENT_DIR + "/models.json"

# The pi version pinned in the Dockerfile. Recording it as the last seen
# changelog keeps pi from opening its changelog screen on first launch.
PI_VERSION = "0.73.1"

PROVIDER = "deepseek"
DEFAULT_MODEL = "deepseek-flash"
API_KEY_ENV = "DEEPSEEK_API_KEY"
VALID_AUTH_TYPES = ("api-key", "auth-file")

# Non-secret provider definition (same models the SLDB desks run on).
DEEPSEEK_PROVIDER: dict[str, Any] = {
    "baseUrl": "https://api.deepseek.com/v1",
    "api": "openai-completions",
    # An env var NAME, resolved by pi at runtime — never the key itself.
    "apiKey": API_KEY_ENV,
    "models": [
        {
            "id": "deepseek-flash",
            "name": "DeepSeek V4.1 Flash",
            "reasoning": True,
            "input": ["text", "image"],
            "contextWindow": 1048576,
            "maxTokens": 393216,
        },
        {
            "id": "deepseek-v4-pro",
            "name": "DeepSeek V4 Pro",
            "reasoning": True,
            "input": ["text"],
            "contextWindow": 1048576,
            "maxTokens": 393216,
        },
    ],
}

AUTH = sh.AuthSpec(
    harness="pi",
    methods=[
        sh.env_method("api-key", any_of=[API_KEY_ENV], hint=f"set {API_KEY_ENV}"),
        sh.file_method("auth-file", path=PI_AUTH_FILE, secret_key="PI_AUTH"),
    ],
)


def _load_object(path: str, ctx: sh.ProvisionContext) -> dict[str, Any] | None:
    """Load a JSON object: {} if absent, None if present but unusable."""
    if not os.path.exists(path):
        return {}
    try:
        data = sh.load_json(path)
    except (OSError, ValueError):
        data = None
    if not isinstance(data, dict):
        ctx.warn(f"{path} is not a JSON object and is left unchanged")
        return None
    return data


def _write_models(ctx: sh.ProvisionContext) -> None:
    """Merge providers.deepseek into models.json; other providers are kept."""
    path = sh.expand_path(PI_MODELS_FILE)
    data = _load_object(path, ctx)
    if data is None:
        return
    providers = data.get("providers")
    if not isinstance(providers, dict):
        providers = {}
    providers[PROVIDER] = json.loads(json.dumps(DEEPSEEK_PROVIDER))
    data["providers"] = providers
    sh.atomic_write_json(path, data)


def _resolve_model(ctx: sh.ProvisionContext) -> tuple[str, str]:
    """Return (provider, model). Accepts "model" or "provider/model"."""
    model = sh.resolve_model(ctx) or DEFAULT_MODEL
    provider, sep, model_id = model.partition("/")
    if sep and provider and model_id:
        return provider, model_id
    return PROVIDER, model


def _write_settings(ctx: sh.ProvisionContext, provider: str, model: str) -> None:
    """Shallow merge: scion owns defaultProvider/defaultModel, keeps the rest."""
    path = sh.expand_path(PI_SETTINGS_FILE)
    data = _load_object(path, ctx)
    if data is None:
        return
    data["defaultProvider"] = provider
    data["defaultModel"] = model
    data.setdefault("lastChangelogVersion", PI_VERSION)
    sh.atomic_write_json(path, data)


def _write_auth_file(ctx: sh.ProvisionContext) -> bool:
    """Install the staged PI_AUTH secret as ~/.pi/agent/auth.json (0600)."""
    if "PI_AUTH" not in ctx.file_secret_files:
        return False
    content = ctx.read_file_secret("PI_AUTH")
    if not content.strip():
        raise sh.ProvisionError("PI_AUTH secret is empty")
    try:
        json.loads(content)
    except json.JSONDecodeError as exc:
        raise sh.ProvisionError(f"PI_AUTH secret is not valid JSON: {exc}") from exc
    sh.atomic_write_text(sh.expand_path(PI_AUTH_FILE), content, mode=0o600)
    return True


def provision(ctx: sh.ProvisionContext) -> None:
    explicit = ctx.explicit_type
    if explicit and explicit not in VALID_AUTH_TYPES:
        raise sh.ProvisionError(
            f"pi: unknown auth type {explicit!r}; "
            f"valid types are: {', '.join(VALID_AUTH_TYPES)}"
        )
    resolved = ctx.select_auth(AUTH)

    extra: dict[str, Any] = {}
    if resolved.method == "auth-file":
        extra["auth_file_written"] = _write_auth_file(ctx)

    ctx.write_outputs(resolved, env={}, extra=extra)

    _write_models(ctx)
    provider, model = _resolve_model(ctx)
    _write_settings(ctx, provider, model)

    ctx.info(f"method={resolved.method} provider={provider} model={model}")


if __name__ == "__main__":
    sh.run("pi", provision)
