# Research and Writing Implementation Plan

> Execute inline with superpowers:executing-plans; review the whole change after validation.

**Goal:** Replace the two placeholder runners with shared evidence-bound research and complete assigned writing.
**Architecture:** Shared hub text worker, evidence validation and idempotent Drive adapter; thin lane entrypoints.
**Tech Stack:** Python 3.11+, existing requests/filelock/Hermes CLI and unittest.
**Spec:** docs/superpowers/specs/2026-10-24-research-writing-design.md

## Global Constraints
No merge, deploy, delete files, visibility change or publication. Local models and free tools only. Preserve source originals and production commands. Research saved before writer claim; real Drive readback before completion.

## Review Focus
Missing host dependencies fail before agent invocation; stale source hashes block; cross-lane claims block; conflicting retries preserve inputs; partial upload recovery reuses matching remote objects.

### Task 1: Real Drive adapter
Files: src/drive_storage.py, tests/test_rotation.py.
- [x] Write failing identity/readback tests.
- [x] Add upload/readback with stable content identity and SHA256; reject conflicts and wrong parents.
- [x] Run the relevant tests and existing suite.

### Task 2: Shared text worker and edition research
Files: src/text_rotation.py, tests/test_rotation.py, config/text_tools.example.json.
- [x] Write failing source validation, missing runtime, immutable retry and handoff tests.
- [x] Add writing-only Hermes preflight, frozen source/catalog staging, report validation and Drive-before-handoff flow.
- [x] Run relevant tests and suite.

### Task 3: Assignment writers and adapters
Files: src/text_rotation.py; private runner src/runner.py and tests; docs/TEXT_ROTATION.md.
- [x] Test exclusive claims, complete lane files, review/hash gates, resume and CLI delegation.
- [x] Implement shared writing; wire Master Research daily/sunday and Glitch write; add Psychology assignment command preserving existing commands.
- [x] Run all suites, compile and diff checks; attempt real preflight; review.
- [x] Open repair PRs, record precise runtime blockers and handoff note. No merge.
