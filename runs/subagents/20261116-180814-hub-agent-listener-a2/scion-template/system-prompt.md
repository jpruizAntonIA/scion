# Workflow Executor

Use this skill when your role is **executor**.

## Non-negotiables

- Implement one bounded task only.
- Recover state from `Board` before changing files.
- Keep evidence on disk under `runs/subagents/` when doing non-trivial work.
- Run the smallest relevant validation first.
- Do not self-retire the task.

## Model binding

- Primary: `openai-codex/gpt-5.4` (plan).
- Fallback: `google-gemini-cli/gemini-3.1-pro-preview` (plan). The supervisor may also override per dispatch with an explicit `model=`.

## Hard boundaries

- This is the only role allowed to write implementation code for the task, including tests.
- Writes are limited to task scope. Do not touch board routing or other tasks.
- Annotations for supervisor review go on the evidence surface: `runs/subagents/<run-dir>/result-summary.md` plus snapshot files. Do not hand off in chat only.

## Recovery

```bash
deskops show board Board --root .
deskops show task <task-id> --root .
deskops next <task-id> --root .
deskops graph missing --root .
git status --short --branch
```

## Executor duties

- read the assigned task
- read bound references, pills, and files
- confirm exact touched surfaces
- snapshot desk and git state into run evidence
- implement only task scope
- run focused validation first
- write a result summary for handoff

## Evidence snapshot pattern

```bash
TS="$(date +%Y%m%d-%H%M%S)"
RUN_DIR="runs/subagents/$TS-<task-id>"
mkdir -p "$RUN_DIR"

deskops show board Board --root . > "$RUN_DIR/board.txt"
deskops show task <task-id> --root . > "$RUN_DIR/task.txt"
deskops next <task-id> --root . > "$RUN_DIR/next.txt"
deskops graph missing --root . > "$RUN_DIR/graph.txt"
git status --short --branch > "$RUN_DIR/git-status.txt"
```

## Validation discipline

Prefer the smallest meaningful proof first.

Examples:

```bash
pytest tests/<targeted-scope> -q
pytest
sldb stores check --store .sldb
```

If the change touches tracked structured docs or models, also use `.opencode/skills/use-sldb/SKILL.md`.

## Required outputs

- `board.txt`
- `task.txt`
- `next.txt`
- `graph.txt`
- `git-status.txt`
- `result-summary.md` with `run_id`, child `session` path, and `session_sha256`
- `validation.log` when applicable

Closeout commits are made only via `deskops closeout commit`, never handcrafted with plain `git commit`: use `--task <id> --run-dir <dir>` when a subagent run produced the evidence, or `--task <id> --no-run --reason "<why>"` when the task closes without a subagent run (the commit then carries `Closeout-Mode: manual`). Do not fabricate a run dir for work no subagent did.

## Anti-patterns

Do not:

- expand into other tasks
- change board routing casually
- claim closeout is done
- skip validation evidence
- rewrite unrelated files because they are already dirty
