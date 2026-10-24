# Linux worker

The repository now has an installable, bounded Linux execution path. This is a CPU worker runtime, not a provisioned GPU farm or a completed video.

`scripts/bootstrap_cpu_worker.sh /absolute/runtime` installs pinned official Hermes and llama.cpp, checks model/voice downloads against SHA-256 values, and writes `worker.json` plus a media-tool manifest. It requires git, curl, GCC/G++, FFmpeg, ffprobe and uv 0.13.4. The model is Qwen3-4B Q4_K_M (Apache-2.0); the optional Piper voice uses the public-domain LJ Speech dataset. Licenses stay with the installation.

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

The manual `production` mode also calls the production command with unchanged gates. It is expected to fail while full-review capabilities remain absent. The automatically triggered branch acceptance uses `runtime` mode only. If the repository becomes private, re-evaluate the account's Actions billing before running this workflow.

## Source identity

The narration is extracted verbatim from the eight VOICEOVER sections of "Dark Psychology for High Intelligence: The Mind Games Most People Never See". Source: https://drive.google.com/file/d/1sJXFLjvYzefCpI6iE1N3UaQF6DQaFxvf/view

Narration SHA-256: `dc079f5e3b113a84e880e8b40190a1d93b16a7b6ef84452706e731f2efcbd05b`.

The source's five-minute scene labels do not define real speech duration. The earlier local Piper synthesis measured 119.698866 seconds and was not perceptually reviewed. The source contains broad psychological claims; preserve the text for this test and keep factual/owner review outstanding before release.
