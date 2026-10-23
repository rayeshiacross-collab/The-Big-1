# End-to-End Dry Run (Reference)

Design reference, not a completed farm integration. See HARDENING.md for implemented gates and missing adapters.

**Example subject:** “Why a promotion can feel like a loss when it costs autonomy, evenings, and caregiving capacity”

## 1. Master Research (DC) — 06:00 CT

Skills: `dc-daily-signals` → `dc-rank-candidates` → `dc-assignment-handoff`

Creates handoff:
```yaml
run_id: 20261022-0600-central
content_id: psych-20261022-autonomy-cost
target_lane: psychology
selected_angle: "A promotion that costs autonomy, evenings, and caregiving capacity often feels like a net loss even when the title and pay look better."
research_completion_status: RESEARCH_COMPLETE
```

## 2. Psychology Runner

Skills: `psych-flagship-script` → `psych-shorts-trio` → `psych-companion-article` → `psych-quality-gate`

Produces:
- Flagship script (~1,300–1,500 words)
- Three distinct Shorts
- Companion article
- Production notes

Status → `WRITING_COMPLETE`

## 3. Hypit

Skills: `hypit-packaging` → `video-from-script` → `hypit-quality-gate`

Produces:
- Titles, description, keywords, pinned comment
- Thumbnail concepts (cyberpunk motion graphics; no host / no cyborg)
- Full scene-by-scene video production package (open tools only)

Status → `RENDER_PENDING`

## 4. Omni (parallel)

Skills: `omni-rss-adapter` → `omni-podcast-adapter` → quality gate

Produces RSS + podcast versions linked by the same content_id.

## 5. You

Review everything in Drive.  
Only you set `RELEASE_APPROVED`.

Nothing publishes automatically.
