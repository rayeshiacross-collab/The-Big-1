# Portable worker implementation plan

Goal: make The-Big-1 executable on a standard Linux worker without depending on the chat session's restricted Unix sockets.

Architecture: install official pinned Hermes, llama.cpp and an integrity-checked Apache-2.0 local model; start inference on loopback for the lifetime of one job; execute the existing production entrypoint with real installed media tools. Preserve source, private logs and failure status. No publishing or fabricated review receipts.

Execution: inline, as directed by the owner to build and run the machine.

- [x] Add and verify tests for service readiness, early process failure, timeout cleanup and missing tool-use proof.
- [x] Implement managed local inference and a live Hermes tool-use acceptance command.
- [x] Add reproducible Linux bootstrap, manual worker workflow and source-specific acceptance input.
- [x] Run local regression checks, review changes, save a repair branch/PR and execute the Linux acceptance job.

Constraints: existing production validation stays unchanged; missing full audio/video perception remains blocking. Standard public-repository Linux runner only; no larger/GPU paid runner. Read-only workflow permissions. No inherited secrets in Hermes or inference subprocesses. Runtime acceptance does not mean production-video acceptance.

Ruling: use a new branch in this task-owned checkout; preserve untracked production-test evidence and all existing files.

Verification: 45 local tests passed; shell syntax and whitespace checks passed. Fresh reviewer identified and fixes addressed fresh-clone refusal, invalid readiness URL, detached gateway cleanup and port collision. First live Linux run exposed Hermes's 64,000-token context minimum; configuration now uses the 262,144-context Qwen3-4B-Instruct-2507 model with a 65,536-token server window. Second Linux run 40077065924 passed live Hermes tool use and exact-script speech synthesis. Full video rendering/perception remains outside this completed runtime slice and is still unfinished.

## Media continuation

- [x] Add an explicit assembly checkpoint to the existing producer, sharing all media validations with full production and never creating verified-delivery or perception claims.
- [x] Add CPU Manim renderer to the pinned bootstrap and branch assembly execution.
- [ ] Execute real script-only Hermes assembly, inspect actual media, repair failures and preserve the MP4.
- [ ] Complete genuine full video/audio perception before any reviewed-complete claim.
