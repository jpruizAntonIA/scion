# pi Harness Bundle

Scion harness configuration for [pi](https://www.npmjs.com/package/@mariozechner/pi-coding-agent)
(`@mariozechner/pi-coding-agent`), a terminal coding agent. The bundle runs pi
against DeepSeek by default (`deepseek-flash`).

## Install

```sh
scion harness-config install harnesses/pi
```

## Build the image

```sh
scion build pi
```

The Dockerfile builds `FROM ${BASE_IMAGE}` (scion-base, which already ships
node 24), checks node >= 20.6 and installs pi pinned to `0.73.1`
(`--build-arg PI_VERSION=...` to change it). No credential is baked into the
image.

## Auth Modes

| Mode | Env / File | Notes |
|------|-----------|-------|
| `api-key` (default) | `DEEPSEEK_API_KEY` | `models.json` stores the env var *name*; pi reads the key at runtime |
| `auth-file` | `PI_AUTH` → `~/.pi/agent/auth.json` (0600) | a pi-native `auth.json` (where pi stores API keys and `/login` tokens) |

With neither, the agent drops to a shell (`no_auth: drop-to-shell`): run `pi`,
use `/login`, then `python3 /home/scion/.scion/harness/capture_auth.py`.

Register the key with scion (never copy a host `~/.pi/agent/auth.json` or
`secrets.env` into the image or the repo).

## What provision.py writes

At pre-start, inside the container:

- `~/.pi/agent/models.json`: `providers.deepseek` (base URL
  `https://api.deepseek.com/v1`, `openai-completions`, models `deepseek-flash`
  and `deepseek-v4-pro`, `apiKey: "DEEPSEEK_API_KEY"`). Other providers in the
  file are kept.
- `~/.pi/agent/settings.json`: `defaultProvider`/`defaultModel` from the
  resolved model (always overwritten); every other key is kept.
  `lastChangelogVersion` is set only when absent, so pi skips its changelog
  screen on first launch.
- `~/.pi/agent/auth.json` in `auth-file` mode only.

## Models

`SCION_MODEL` resolves through `model_aliases`:

| Alias | Model |
|-------|-------|
| `small`, `medium` | `deepseek-flash` |
| `large`, `extra-large` | `deepseek-v4-pro` |

A concrete id (`deepseek-v4-pro`) or `provider/model` is passed through. The
model is set in `settings.json`, not on the command line, so that the alias
applies (`pi --model` would override it).

## Resume

`resume_flag: --continue`: a resumed agent runs `pi --continue`, which reopens
pi's most recent session for the workspace.

## Limits

pi has no hook events and no MCP client, so scion cannot enforce `max_turns`
or `max_model_calls`, emit telemetry, or register MCP servers (see
`capabilities` in `config.yaml`). Readiness uses a fixed `delay` settle.

## Tests

```sh
python3 harnesses/pi/provision_test.py
```
