# Research/writing repair validation — October 24, 2026

Implemented inline against existing hub and lane contracts. Independent read-only review identified three defects, each reproduced before correction:

1. Edited evidence/catalog could bypass the research-completion binding. Now the completion ledger records hashes of the full evidence, research report and manifests; every writer verifies that binding before claim/invocation. The original source hash check remains too.
2. An edited report angle could differ from the saved handoff. The full report digest and explicit selected angle/lane/source/catalog comparison bind the writer input to that handoff.
3. Interrupted asset promotion could invoke Hermes again. The validated attempt and its hashes are persisted before the first copy; explicit resume finishes promoting that exact attempt.

Regression tests cover the three failures, failed upload/resume, wrong lane, stale review, source snapshot/date checks, Sunday mode isolation, missing Hermes, both complete lane packages, and Drive reuse/create/conflict/readback contracts. Existing media/hub tests remain in the suite. These are synthetic integration fixtures; no fixture is evidence of actual research, Hermes review or cloud saves.

Operational preflight actually ran and failed with `Hermes is not installed; text rotation has not started`. The default local model endpoint also refused the connection. Required Drive token and folder IDs are absent from this workspace. No real content assignment was claimed, no paid provider used, and no production run/render was made.

Implementation decisions: centralize logic in The-Big-1 and retain thin fixed-lane adapters; process the existing frozen evidence batch without mixing new incoming data; preserve existing Psychology video commands with a separate assignment entrypoint. These choices keep a single shared ledger and preserve current production behavior. The cost is a dependency on the repaired hub and a correctly configured persistent host.

No merge, deployment, repository-file deletion, publication or visibility change. Source-discovery scheduling, host provisioning and token refresh are outside this repair. The next run requires the real host/runtime and actual evidence/catalog paths; source checks here do not establish those exist.
