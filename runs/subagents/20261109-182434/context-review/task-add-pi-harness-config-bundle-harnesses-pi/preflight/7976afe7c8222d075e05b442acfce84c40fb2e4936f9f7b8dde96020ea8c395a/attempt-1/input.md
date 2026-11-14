FILE:desk/tasks/task-add-pi-harness-config-bundle-harnesses-pi.md
---
sldb:
  by: agent
  at: '2026-11-09T18:24:17Z'
  authority: generated
  via: create_document
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

(1) Dockerfile: FROM ${BASE_IMAGE}; ensure node >= 20.6 (fail the build if older); npm install -g @mariozechner/pi-coding-agent with the same npmrc secret mount + cache clean as opencode; create /home/scion/.pi/agent owned by scion. (2) config.yaml: harness pi, image scion-pi:latest, user scion, container-script provisioner like opencode, config_dir .pi/agent, interrupt_key C-c, ready strategy delay, delivery submit_keys [Enter], instructions_file AGENTS.md (pi reads AGENTS.md), command.base ["pi","--provider","deepseek","--model","deepseek-flash"] with model selection overridable via model_aliases (small/medium -> deepseek-flash, large/extra-large -> deepseek-v4-pro), resume_flag --continue, honest capabilities (mark unsupported features "no" with a reason), auth default_type api-key with required_env DEEPSEEK_API_KEY plus an auth-file type targeting .pi/agent/auth.json, autodetect for both. (3) provision.py (scion_harness lib): write ~/.pi/agent/settings.json (defaultProvider deepseek, defaultModel) and ~/.pi/agent/models.json defining provider deepseek (baseUrl https://api.deepseek.com/v1, api openai-completions, models deepseek-flash and deepseek-v4-pro) whose apiKey is the env var NAME "DEEPSEEK_API_KEY" (pi resolves it at runtime; no secret on disk) in api-key mode; in auth-file mode install the scion-staged auth file to ~/.pi/agent/auth.json mode 0600. Merge, do not clobber, pre-existing user keys in settings.json. (4) provision_test.py: unittest covering both auth modes, no-auth, idempotency, merge behaviour, file modes, and that no secret value is written into models.json/settings.json. (5) README.md: install, build, auth modes, model aliases, resume.

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

Bundle committed locally on wt/pi-harness, schema install passes, provision_test passes, vendored lib byte-identical, image builds; the live smoke is either passed or explicitly blocked only on JP registering the DeepSeek key.

FILE:instruccion
Preflight solo-TaskDoc de la tarea task-add-pi-harness-config-bundle-harnesses-pi: reformula el encargo tal como lo leería un ejecutor sin ningún otro contexto, lista ambigüedades con cita textual del input y da el DRY-RUN sin ejecutar nada. No ejecutes nada.

