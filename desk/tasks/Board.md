---
# board-xxx
id: board-001
# Affected workspace or domain
scope: desk
# List of task-xxx paths
tasks:
- desk/tasks/task-add-pi-harness-config-bundle-harnesses-pi.md
# List of pill-xxx paths
pills:
- desk/contexts/pills.md
# List of ritual-xxx paths
rituals:
- desk/rituals/phase.md
- desk/rituals/execution.md
- desk/rituals/testing.md
- desk/rituals/closeout.md
# e.g., system:sldb, workspace:desk
tags:
- workspace:desk
---

# scion Board

## Purpose

_Explain what this board routes and why it exists._

Route the active execution set for scion.

## Notes

_Add short operational notes about the current routed set._

Bootstrap complete. Add active task docs under `desk/tasks/` and route them here.

## Task Details

_Generated from the task references above._

- Add pi harness-config bundle (harnesses/pi) [draft] - A new harness-config bundle harnesses/pi/ that scion can install, build into an image, provision inside the container, and run as an agent with DeepSeek Flash by default, including stop + resume of the pi session.
