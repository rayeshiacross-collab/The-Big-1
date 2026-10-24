# Linux worker

The repository now has an installable, bounded Linux execution path. This is a CPU worker runtime, not a provisioned GPU farm or a completed video.

`scripts/bootstrap_cpu_worker.sh /absolute/runtime` installs pinned official Hermes and llama.cpp, checks model/voice downloads against SHA-256 values, and writes `worker.json` plus a media-tool manifest. It requires git, curl, GCC/G++, FFmpeg, ffprobe, uv 0.13.4 and the Manim build dependencies `libcairo2-dev libpango1.0-dev libopenblas-dev pkg-config fonts-dejavu-core` (Ubuntu apt packages). The model is Qwen3-4B-Instruct-2507 Q4_K_M (Apache-2.0, Unsloth GGUF conversion of the official Qwen model), served with 65,536 context tokens and F16 KV caches (the worker needs 16 GB RAM). Hermes requires at least 64,000 tokens; this model's native context is 262,144. The optional Piper voice uses the public-domain LJ Speech dataset. Licenses stay with the installation.

Run a live model-backed tool-use acceptance test:

```bash
/absolute/runtime/worker-env/bin/python -m src.worker_runtime \
  --runtime /absolute/runtime/worker.json --output /persistent/attempt
```

This owns the model process, uses loopback-only inference, launches isolated Hermes, and requires an actual tool-created nonce file. A verbal "success" cannot pass. A runtime pass is `RUNTIME_READY`, with `production_video_complete: false` and `published: false`.

Full production uses the existing validator:

```bash
/absolute/runtime/worker-env/bin/python -m src.worker_runtime \
  --runtime /absolute/runtime/worker.json --output /persistent/attempt \
  --content-id psych-20261024-dark-psychology-test \
  --script examples/dark-psychology/narration.txt \
  --policy examples/dark-psychology/policy.json \
  --tools /absolute/runtime/media-tools.json
```

The bootstrap registers real Piper and FFmpeg executables. It does **not** claim to install semantic full-video or full-audio perception tools. Until real review tools are integrated, production fails explicitly at that gate. FFmpeg decoding, ASR or sampled frames must not be represented as full playback review. No receipt is fabricated and no release approval is supplied.

## GitHub execution

`Linux worker acceptance` runs on a standard `ubuntu-24.04` public-repository VM. It installs the runtime, verifies a real Hermes tool call and synthesizes the exact test narration. Its artifact retains status, logs and audio for seven days. This VM is ephemeral and has no GPU. It does not register a persistent self-hosted runner, publish anything or expose a public model endpoint.

The manual `production` mode also calls the production command with unchanged gates. It is expected to fail while full-review capabilities remain absent. The automatically triggered branch acceptance runs the assembly checkpoint directly; manual runtime mode performs the separate nonce check. If the repository becomes private, re-evaluate the account's Actions billing before running this workflow.

## Verified Linux execution — 2026-10-24

Run https://github.com/rayeshiacross-collab/The-Big-1/actions/runs/40077065924 passed on commit `812fe9e1054330848bf0853e5cb00e49ece4cd50`.

- Fresh installation passed.
- Local model-backed Hermes created and read the random tool-proof file.
- Scoped gateway shutdown passed.
- The exact narration synthesized and fully decoded; measured audio duration: 119.524717 seconds.
- Retained worker status: `RUNTIME_READY`, `live_tool_use: true`, `production_video_complete: false`, `published: false`.
- Full production step was skipped in runtime mode. No MP4 was generated and no semantic full-playback review was performed.
- All 45 Python regression tests passed locally and the branch's GitHub regression checks passed.

The first Linux run failed because the earlier model server exposed only 16,384 context tokens. That attempt is retained separately and was corrected by the long-context model configuration above.

## Narration source

The narration is extracted verbatim from the eight VOICEOVER sections of "Dark Psychology for High Intelligence: The Mind Games Most People Never See". Source: https://drive.google.com/file/d/1sJXFLjvYzefCpI6iE1N3UaQF6DQaFxvf/view

Narration SHA-256: `dc079f5e3b113a84e880e8b40190a1d93b16a7b6ef84452706e731f2efcbd05b`.

The source's five-minute scene labels do not define real speech duration. The earlier local Piper synthesis measured 119.698866 seconds and was not perceptually reviewed. The source contains broad psychological claims; preserve the text for this test and keep factual/owner review outstanding before release.

## Assembly checkpoint

`--assembly-only` on the existing production and worker commands runs Hermes authoring and real media validation before the separate playback-review stage. It saves `assembly_report.json` with `ASSEMBLED_NOT_REVIEWED`, never `verified_delivery.json`. All seven assets, exact-source narration/captions/scene coverage, H.264 dimensions/frame rate, audio presence/duration, full decoding, temporal motion and metadata constraints remain required. Default full production still requires actual full audio/video perception and self-QA.

The bootstrap now installs Manim Community 0.22.0 with its CPU Cairo renderer. The branch workflow performs an assembly attempt automatically; manual runtime, assembly and full production modes are also available. A successful assembly is not a completed production test or release approval.

The first assembly job timed out during a redundant nonce check: Q8 CPU prompt processing took 521 seconds for 4,893 tokens. The nonce file was actually created, but the CLI exceeded its deadline before final completion. CPU builds now enable native instructions and OpenBLAS and use F16 attention caches; runtime-only checks have a 20-minute deadline. Production goes directly through real Hermes authoring after model readiness, rather than performing two extra nonce conversations. These changes still require live verification.

The second assembly attempt reached Hermes, which reported that no all-in-one generator was installed despite available component tools. The worker now exposes a mechanical `assembly-helper`: timed exact-source Piper speech, editable SRT, measured paragraph intervals, and encoding/caption burn-in/thumbnail extraction from Hermes-authored animation. The helper supplies no scene choices and no perception attestations. Its speech path was exercised on the real script locally (127.916 seconds); it still awaits actual Hermes scene production.

The helper-enabled attempt exposed a gateway working-directory mismatch: the script existed in the attempt directory but the agent searched elsewhere. Production invocation now passes the official `--in` workspace option, a scoped `TERMINAL_CWD`, and explicit absolute input/output paths. A regression test verifies all three handoffs.
