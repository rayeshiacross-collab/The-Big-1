# REBOOTv2 — One-Page Map

**One farm. Five workers. Hermes + open-source only. Nothing ships without you.**

---

## The five lanes

| # | Lane | Repo | Job in one line |
|---|------|------|-----------------|
| 1 | **Master Research (DC)** | `rebootv2-master-research` | Find, verify, rank, assign today’s subjects |
| 2 | **Psychology** | `rebootv2-psychology-runner` | Long-form script + 3 Shorts + companion article |
| 3 | **System Glitch** | `rebootv2-system-glitch-runner` | 25–35s short that reveals one digital contradiction |
| 4 | **Hypit** | `rebootv2-hypit` | If it goes in, it gets advertised — commercials, thumbs, draft distribution packages; no live connector execution |
| 5 | **Omni** | `rebootv2-omni` | RSS, blogs, newsletters, podcasts (non-YouTube long-form/audio) |

Central hub: **`The-Big-1`** — architecture, open-stack rules, skeleton code, this map.

---

## Daily flow

```
06:00 CT     DC runs → research + handoffs (content_id)
                ↓
         Psychology  +  System Glitch  (in parallel)
                ↓              ↓
         full package      short package
                ↓              ↓
              Hypit  ← packages, commercials, thumbs, distribution
                ↓
              Omni   ← RSS / podcast when needed
                ↓
         Everything in Drive / Harvest
                ↓
         YOU review → RELEASE_APPROVED only
```

---

## Hard rules (never break)

| Rule | Meaning |
|------|--------|
| Open stack only | Local models, ComfyUI, open TTS — no paid APIs by default |
| No host / no cyborg | Cyberpunk motion graphics only |
| content_id is forever | Same ID from research through every ad and RSS version |
| Quality gates fail closed | Partial work stays draft |
| No auto-publish | You are the only release gate |
| Hypit advertises everything | Book list = commercial + thumbs **per title**; every enabled social/tool gets a package |

---

## Status path (global)

`RESEARCH_COMPLETE` → `WRITING_IN_PROGRESS` → `WRITING_COMPLETE` → `RENDER_PENDING` → `VIDEO_QA_PASSED` → **`RELEASE_APPROVED`** (you only)

---

## Where things live

| Place | What |
|-------|------|
| **Daily Intelligence** (Drive) | DC reports, handoffs, source ledgers |
| **REBOOTv2 production** | Scripts, shorts, production packages |
| **Hypit packaging** | Commercials, thumbs, distribution plans |
| **Omni** | RSS / podcast adaptations |
| **Harvest** | What you open to review |

---

## Planned distribution packages (Hypit)

Socials: YouTube, Instagram, TikTok, X, Facebook, Threads, LinkedIn, **Pinterest**, **Blogger**, other blogs, RSS  
Potential destinations: **Metricool**, **Zapier**. This hub has no publishing connector, and no connection or approval enforcement in the lane repos is certified here.  
Config: `rebootv2-hypit/config/socials.yaml`

---

## Stack in one breath

Hermes Agent · local LLMs (Ollama / llama.cpp / vLLM) · open image/video (ComfyUI) · open TTS · GitHub · Drive · your approval

---

*Descriptions of each lane and the video style can be dropped in when ready — this map stays the single page of truth.*
