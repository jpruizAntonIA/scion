---
sldb:
  by: agent
  at: '2026-11-09T18:25:26Z'
  authority: generated
  via: save_document_payload
id: task-add-pi-harness-config-bundle-harnesses-pi
status: draft
summary: ''
tags:
- workspace:desk
- artifact:task
current_node: ritual-execution
history: []
references: []
depends_on: []
pills: []
files:
- harnesses/pi/config.yaml
- harnesses/pi/Dockerfile
- harnesses/pi/provision.py
- harnesses/pi/provision_test.py
- harnesses/pi/scion_harness.py
- harnesses/pi/capture_auth.py
- harnesses/pi/home/.bashrc
- harnesses/pi/README.md
task_type: task.code
inherits_from: []
inherit_acceptance_context: false
atoms: []
---

# Add pi harness-config bundle (harnesses/pi)

## Rationale

_Explain why this task exists or the business driver behind it._

JP approved moving SLDB_1 work into scion with herdr as the control surface. scion needs `pi` (@mariozechner/pi-coding-agent, the runtime the desks already use with DeepSeek) as a first-class harness.

## Goal

_Describe the concrete result this task must produce._

A new harness-config bundle harnesses/pi/ that scion can install, build into an image, provision inside the container, and run as an agent with DeepSeek Flash by default, including stop + resume of the pi session.

## Scope

_State what is in scope and what is out of scope._

IN: harnesses/pi/ only (config.yaml, Dockerfile, provision.py, provision_test.py, scion_harness.py vendored byte-identical from harnesses/scion_harness.py, capture_auth.py shim, home/.bashrc seed, README.md). Pattern copied from harnesses/opencode/ (closest: npm-installed Node CLI); follow harnesses/authoring-guide.md. OUT: Go host code, other harnesses, the shared scion_harness.py, any push, any real credential. NEVER copy host ~/.pi/agent/auth.json or ~/.pi/agent/secrets.env (or any key) into the image, the bundle or the repo.

## Implementation Path

_Outline the expected implementation route or affected surface._

(1) Dockerfile: FROM ${BASE_IMAGE} (scion-base, built on node:24-trixie-slim, so node/npm are already present: do NOT install node; add a RUN gate that fails the build if node < 20.6); npm install -g @mariozechner/pi-coding-agent@0.73.1 (pinned to the version the desks run on the host) with the same npmrc secret mount + cache clean as opencode; create /home/scion/.pi/agent owned by scion. (2) config.yaml: harness pi, image scion-pi:latest, user scion, container-script provisioner like opencode, config_dir .pi/agent, interrupt_key C-c, ready strategy delay, delivery submit_keys [Enter], instructions_file AGENTS.md (pi reads AGENTS.md), command.base ["pi","--provider","deepseek","--model","deepseek-flash"] with model selection overridable via model_aliases (small/medium -> deepseek-flash, large/extra-large -> deepseek-v4-pro), resume_flag --continue. Capabilities: declare the same keys opencode declares; mark each yes/partial/no from what pi 0.73.1 actually supports (pi --help), with a one-line reason for every partial/no (e.g. no MCP, no oauth, no vertex). Auth: default_type api-key with required_env DEEPSEEK_API_KEY, plus an auth-file type modelled exactly on opencode's (required_files entry, name PI_AUTH, target_suffix /.pi/agent/auth.json; use whatever field value the settings-v1 schema accepts, verified by scion harness-config install), autodetect for both. (3) provision.py (scion_harness lib): write ~/.pi/agent/settings.json and ~/.pi/agent/models.json. models.json defines provider deepseek (baseUrl https://api.deepseek.com/v1, api openai-completions, models deepseek-flash and deepseek-v4-pro with the same non-secret fields the host desks use: deepseek-flash reasoning true input [text,image] contextWindow 1048576 maxTokens 393216; deepseek-v4-pro reasoning true input [text] same limits; these ids are the ones the host desks already call successfully) whose apiKey is the env var NAME DEEPSEEK_API_KEY (pi resolves it at runtime; no secret on disk) in api-key mode; in auth-file mode install the scion-staged auth file to ~/.pi/agent/auth.json mode 0600. Merge rule: settings.json is a shallow top-level merge (scion sets defaultProvider/defaultModel, every other existing key preserved); models.json merges at providers level (scion owns providers.deepseek, other providers preserved). (4) capture_auth.py: the same 1-line shim as harnesses/opencode/capture_auth.py (sys.exit(scion_harness.capture_auth_main())). (5) provision_test.py: unittest covering both auth modes, no-auth, idempotency, the merge rules above, file modes, and that no secret value is written into models.json/settings.json. (6) README.md: install, build, auth modes, model aliases, resume. Build and smoke are run by the coordinator, not the executor (the coordinator gates scion build on IO pressure avg60 < 30).

## Validation

_List the checks required before this task can close._

- scion harness-config install harnesses/pi (in a scratch HOME or ~/lab-scion) validates the schema without errors
- TMPDIR=/dev/shm timeout 900 systemd-run --user --scope -q -p MemoryMax=2G -- python3 harnesses/pi/provision_test.py passes
- cmp harnesses/scion_harness.py harnesses/pi/scion_harness.py (Go is not installed on this machine, so vendored_lib_test.go cannot run; byte-equality is the substitute)
- scion build of the pi image succeeds (coordinator runs it only when IO pressure allows)
- smoke in ~/lab-scion: scion start --harness pi starts an agent; scion look shows pi ready; scion message gets a reply; stop + resume continues the session (needs JP to register the DeepSeek key in scion)
- grep finds no API key literal and no copy of host auth.json/secrets.env anywhere under harnesses/pi

## Done When

_Name the observable condition that makes the task complete._

Bundle committed locally on wt/pi-harness, schema install passes, provision_test passes, vendored lib byte-identical, image builds; the live smoke is either passed or explicitly blocked only on JP registering the DeepSeek key. Smoke resume criterion: before stop, tell the agent a codeword via scion message; after stop + resume (pi --continue), asking for the codeword returns it.
