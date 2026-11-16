---
sldb:
  by: agent
  at: '2026-11-16T05:15:05Z'
  authority: generated
  via: save_document_payload
# review-<task>-<kind>-<n>
id: review-task-hook-deskops-tools-venv-de-test-del-repo-de-la-tarea-pytest-pytest-xdist-y-extras-de-test-dentro-del-evidence-commit-1
# preflight | bundle | reproduction | goldens | owner | node | evidence
kind: evidence
# kind evidence only: tests | commit | atom | materialization | document | external
fact: commit
# kind evidence only: what the producer verified, one item per line
value: 748443c8314ba419525dfda9d1facae59484b191
# doc:<Model>:<id> or empty for reviews of plan nodes
subject: doc:TaskCodeDoc:task-hook-deskops-tools-venv-de-test-del-repo-de-la-tarea-pytest-pytest-xdist-y-extras-de-test-dentro-del@sha256:77af7e4b53bff98d6db6fb0a9d5b29f82e1d452746bc41c151fb7d31d0f1aa88
# <plan>/dag.yaml#node:<ID>; empty when subject names a document
subject_ref: ''
# RuntimeProfileDoc name or "human"
engine: deskops-closeout
actor: scion
# Run evidence directory under runs/, relative to the project root
run_dir: ''
input_sha256: ebce5171dad9fe6ac71b584ef3bf54f918fea741596a809e14a9a7e7adfcda09
output_sha256: ''
# pending | accepted | rejected | incomplete
verdict: accepted
reason: 'verified: commit 748443c8314ba419525dfda9d1facae59484b191'
# ISO 8601 timestamp
created_at: '2026-11-16T05:15:01.952499+00:00'
# ISO 8601 timestamp, empty while pending
disposed_at: '2026-11-16T05:15:01.952499+00:00'
disposed_by: scion
# e.g. workspace:desk
tags:
- workspace:desk
---

# Closeout evidence commit of task-hook-deskops-tools-venv-de-test-del-repo-de-la-tarea-pytest-pytest-xdist-y-extras-de-test-dentro-del

## Summary

_Summarize what was reviewed and the evidence this receipt records._

closeout verify checked commit: 748443c8314ba419525dfda9d1facae59484b191

## Disposition

_Record the verdict rationale and who disposed of the review._

Verdict accepted: verified: commit 748443c8314ba419525dfda9d1facae59484b191
