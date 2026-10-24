# Portable worker implementation plan

Goal: make The-Big-1 executable on a standard Linux worker without depending on the chat session's restricted Unix sockets.

Architecture: install official pinned Hermes, llama.cpp and an integrity-checked Apache-2.0 local model; start inference on loopback for the lifetime of one job; execute the existing production entrypoint with real installed media tools. Preserve source, private logs and failure status. No publishing or fabricated review receipts.

Execution: inline, as directed by the owner to build and run the machine.

- [ ] Add and verify tests for service readiness, early process failure, timeout cleanup and missing tool-use proof.
- [ ] Implement managed local inference and a live Hermes tool-use acceptance command.
- [ ] Add reproducible Linux bootstrap, manual worker workflow and source-specific acceptance input.
- [ ] Run local regression checks, review changes, save a repair branch/PR and execute the Linux acceptance job.

Constraints: existing production validation stays unchanged; missing full audio/video perception remains blocking. Standard public-repository Linux runner only; no larger/GPU paid runner. Read-only workflow permissions. No inherited secrets in Hermes or inference subprocesses. Runtime acceptance does not mean production-video acceptance.

Ruling: use a new branch in this task-owned checkout; preserve untracked production-test evidence and all existing files.
