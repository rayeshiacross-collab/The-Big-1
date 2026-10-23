# REBOOTv2 — Open Stack Policy (Mandatory)

**Rule: If an open-source or free alternative exists, we use it. Paid services are forbidden by default.**

## Allowed (preferred)

| Need | Open / Free choice |
|------|--------------------|
| Agent runtime | **Hermes Agent** (MIT) |
| Language models | Local only: Ollama, llama.cpp, vLLM, LM Studio, Unsloth, etc. |
| Image generation | Open weights (Flux open, SDXL, etc.) via ComfyUI or equivalent |
| Video generation | Open pipelines only (ComfyUI + open video models, AnimateDiff, etc.) when ready |
| Text-to-speech | Piper, Coqui TTS, XTTS, StyleTTS2, or other open TTS |
| Web research | Public web, official government sites, arXiv, PubMed, OpenAlex, Reddit public, Google Trends public |
| Scheduling | Hermes built-in cron + GitHub Actions (free tier) |
| Storage | Existing Google Drive + local ledgers |
| Version control | GitHub |
| Secrets | GitHub Secrets / environment variables only |

## Explicitly forbidden by default

- Paid LLM APIs (OpenAI, Anthropic, etc.) unless you explicitly override for a one-off test
- vidIQ, TubeBuddy, or any paid YouTube analytics
- Paid search or trend APIs
- Paid stock footage / music libraries when open alternatives exist
- Any service that requires a credit card for the core daily loop

## How Hermes must behave

1. Prefer local model endpoints.
2. If a local model is unavailable, fail clearly and ask — do not silently fall back to a paid API.
3. All skills assume public sources and open tools only.
4. When generating visuals or video packages, use open prompt formats compatible with ComfyUI / open video pipelines.

## Cost philosophy

The daily production loop must be runnable on a machine you already own (or a cheap free-tier VPS) with zero ongoing API spend.
