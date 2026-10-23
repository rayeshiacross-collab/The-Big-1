# Recommended Local Open Models (No Paid APIs)

## Writing / Reasoning

| Role | Suggested models | Notes |
|------|------------------|-------|
| Daily workhorse | Llama 3.1 8B / 70B Instruct (Q5/Q6), Qwen2.5 14B/32B, Mistral Small / Nemo | Good balance |
| Heavier reasoning | Qwen2.5 32B, Llama 3.1 70B, DeepSeek distill variants | For ranking & complex explanation |
| Fast / cheap | Phi-3.5 / Phi-4 mini, Gemma 2 9B, small Qwen | Titles, quick checks |

## TTS (open)
Piper, Coqui TTS, XTTS, StyleTTS2

## Image / Video (when ready)
ComfyUI + open weights (Flux open, SDXL, AnimateDiff, etc.)

## Rules
1. Try configured local model first
2. Escalate to larger local model only if set
3. If nothing local is reachable → stop and report (never call paid APIs)
