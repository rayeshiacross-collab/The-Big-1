# The-Big-1

**REBOOTv2 — The central control plane**

This is the big one.  
One farm. Five workers. Hermes + open-source only. Nothing ships without you.

This repository provides hardened shared controls and a [script-only Hermes production entrypoint](./docs/AUTONOMOUS_VIDEO.md). With an installed local Hermes/model and real media tools, Hermes independently creates and reviews the video package. This repository does not provision those tools, a running farm, Drive integration or publishing. See [HARDENING.md](./HARDENING.md) for tested scope and limits.

## The Five Lanes

| Lane | Repo | Job |
|------|------|-----|
| 1. Master Research (DC) | [rebootv2-master-research](https://github.com/rayeshiacross-collab/rebootv2-master-research) | Find → verify → assign |
| 2. Psychology & Behavioral | [rebootv2-psychology-runner](https://github.com/rayeshiacross-collab/rebootv2-psychology-runner) | Long-form + 3 Shorts + companion article |
| 3. System Glitch | [rebootv2-system-glitch-runner](https://github.com/rayeshiacross-collab/rebootv2-system-glitch-runner) | Short-form digital-life packages |
| 4. Hypit | [rebootv2-hypit](https://github.com/rayeshiacross-collab/rebootv2-hypit) | Marketing, packaging, video-from-script |
| 5. Omni | [rebootv2-omni](https://github.com/rayeshiacross-collab/rebootv2-omni) | RSS, Podcasts, non-YouTube |

## Core Rules

- **Hermes Agent** is the runtime
- **Open-source / free tools only** (see `OPEN_STACK.md`)
- Drive is source of record — GitHub executes
- Human approval (`RELEASE_APPROVED`) is the only public release gate
- Idempotent: retries resume, never duplicate
- No false success: files + validation + Drive confirm required

## Quick Links

- [Architecture](./ARCHITECTURE.md)
- [Open Stack Policy](./OPEN_STACK.md)
- [Local Models](./LOCAL_MODELS.md)
- [Drive Layout](./DRIVE_LAYOUT.md)
- [Content ID Rules](./CONTENT_ID.md)
- [Troubleshooting](./TROUBLESHOOTING.md)
- [End-to-End Dry Run](./DRY_RUN.md)

## Status Vocabulary (global)

`RESEARCH_COMPLETE` → `WRITING_IN_PROGRESS` → `WRITING_COMPLETE` → `RENDER_PENDING` → `VIDEO_QA_PASSED` → `RELEASE_APPROVED`

---

*Built with Hermes. Runs on open tools. You hold the gate.*

## Research and assigned writing

The completed shared text entrypoint is `python -m src.text_rotation`. See [TEXT_ROTATION.md](docs/TEXT_ROTATION.md) for frozen evidence inputs, real Drive readback, complete lane packages, runtime checks and resume behavior. It processes an existing batch and never publishes.
