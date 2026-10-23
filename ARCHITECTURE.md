# REBOOTv2 Architecture — Five Lanes, One Farm

## The five private repos

1. `rebootv2-master-research` — DC intelligence & assignment
2. `rebootv2-psychology-runner` — long-form + Shorts + companion article
3. `rebootv2-system-glitch-runner` — short-form digital-life
4. `rebootv2-hypit` — packaging, marketing, video-from-script package
5. `rebootv2-omni` — RSS, podcasts, non-YouTube

## Core principles

- **Hermes Agent** is the runtime
- **Open-source / free tools only** (see OPEN_STACK.md)
- **Drive is source of record**; GitHub executes
- **Human approval is the only release gate**
- **Idempotent**: retries must resume, never duplicate
- **No false success**: files + validation + Drive confirm required

## Daily flow (happy path)

```
06:00 CT  DC runs → research + two handoffs
          ↓
          Psychology claims its handoff → writes full package
          System Glitch claims its handoff → writes short package
          ↓
          Hypit receives completed scripts → packaging + video-from-script package
          Omni adapts selected pieces for RSS / podcast
          ↓
          Everything lands in Drive under correct folders
          Status moves to RENDER_PENDING or WRITING_COMPLETE
          ↓
          You review → RELEASE_APPROVED (only you)
```

## Status vocabulary (global)

| Status | Meaning |
|--------|--------|
| RESEARCH_COMPLETE | DC finished and saved handoff |
| WRITING_IN_PROGRESS | Writer claimed the content_id |
| WRITING_COMPLETE | All required written assets passed checks |
| RENDER_PENDING | Written assets exist; no verified finished video yet |
| VIDEO_QA_PASSED | Finished video passed technical + creative review |
| RELEASE_APPROVED | You explicitly authorized public release |

## Handoff contract

```yaml
run_id: "YYYYMMDD-HHMM-central"
content_id: "psych-20261022-autonomy-cost"
target_lane: "psychology" | "system-glitch" | "hypit" | "omni"
selected_angle: "one clear sentence"
source_urls: [...]
catalog_collision: {...}
required_assets: [...]
research_completion_status: "RESEARCH_COMPLETE"
created_at: "ISO-8601"
```

## Failure & recovery rules

- Network / model / Drive failures are recorded, never silently ignored
- Retry must re-claim the same content_id and resume
- Never create a second episode for the same content_id
- Partial work stays in draft until quality gate passes
- Hermes must fail loudly if a local model or required open tool is missing

## What is deliberately NOT automated

- Publishing to YouTube, Metricool, or any public platform
- Changing live videos
- Spending money on APIs

## Implementation boundary

This is the desired farm architecture. The hub currently certifies only local exclusive claiming, writing validation and gated completion hooks. It does not implement human release approval, publishing, actual Drive transfer, rendering, video QA or the five lane runtimes. Automated helpers refuse RELEASE_APPROVED. No lane repo integration is certified by hub tests.
