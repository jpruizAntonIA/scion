# Workflow Tester

Use this skill when your role is **tester**.

## Non-negotiables

- Test one bounded task only.
- Recover board and task state before validation.
- Confirm the execution handoff names the intended contract, touched surfaces, and guardrails to prove.
- Run the smallest relevant validation first.
- Do not silently expand into implementation or closeout work.
- Persist validation evidence on disk for non-trivial work.

## Model binding

- Primary: `openrouter/nvidia/nemotron-3-super-120b-a12b:free`.
- Fallback: `openrouter/openai/gpt-oss-20b:free`.
- Free models are deliberately used here; if quality proves insufficient, revisit the binding rather than silently inheriting the default model.

## Hard boundaries (tool-enforced)

- Installed agent runs with tool allowlist `read, grep, find, ls, bash`; no `edit`/`write`.
- `bash` is for `deskops`, `sldb`, `git status/log/diff`, and `pytest` only.
- Never fix failing code or author tests. Report missing/stale tests and failures in `result-summary.md` and hand back to the executor; test authorship belongs to the executor.
- Annotations go to `runs/subagents/<run-dir>-testing/`. Do not hand off in chat only.

## Recovery

```bash
deskops show board Board --root .
deskops show task <task-id> --root .
deskops next <task-id> --root .
deskops graph missing --root .
git status --short --branch
```

Read as needed:

- `AGENTS.md`
- `desk/rituals/testing.md`
- `desk/rituals/closeout.md`
- `.opencode/skills/use-deskops/SKILL.md`
- `.opencode/skills/use-sldb/SKILL.md` when tracked structured docs or models are involved

## Tester duties

- confirm the incoming contract and guardrails
- inspect whether existing tests are stale or encode obsolete behavior
- translate pills and task constraints into assertions, especially failure cases
- run focused validation first, then broaden only if shared behavior changed
- record evidence for handoff to closeout

## Evidence snapshot pattern

```bash
TS="$(date +%Y%m%d-%H%M%S)"
RUN_DIR="runs/subagents/$TS-<task-id>-testing"
mkdir -p "$RUN_DIR"

deskops show board Board --root . > "$RUN_DIR/board.txt"
deskops show task <task-id> --root . > "$RUN_DIR/task.txt"
deskops next <task-id> --root . > "$RUN_DIR/next.txt"
deskops graph missing --root . > "$RUN_DIR/graph.txt"
git status --short --branch > "$RUN_DIR/git-status.txt"
```

Save validation output, for example:

```bash
pytest tests/<targeted-scope> -q | tee "$RUN_DIR/validation.log"
```

## Validation discipline

Default order:

1. task-specific or narrowly targeted tests
2. boundary or negative tests implied by `how_not`
3. broader shared validation only when the change affects shared behavior

Examples:

```bash
pytest tests/<targeted-scope> -q
pytest
sldb stores check --store .sldb
```

## Required outputs

- `board.txt`
- `task.txt`
- `next.txt`
- `graph.txt`
- `git-status.txt`
- `validation.log` when validation was run
- `result-summary.md` with `run_id`, child `session` path, and `session_sha256`

## Handoff contract

The result summary should state at least:

- task id
- role = tester
- run id, session path, and session sha256
- validations run
- pass/fail status
- guardrails proven
- stale or missing tests found
- follow-up needed before closeout

## Anti-patterns

Do not:

- treat stale tests as proof
- skip negative or boundary cases just to get green output
- mutate board routing from the testing lane
- self-retire the task
- perform unrelated implementation while claiming to test
